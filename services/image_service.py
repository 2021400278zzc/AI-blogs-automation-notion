"""
图片生成服务
支持多种图片生成 API 格式：
- Pollinations.ai（免费，无需 API Key）
- OpenAI DALL-E 格式（适用于 DALL-E 2/3 及兼容 API）
- Stability AI 格式
- Replicate 格式
- 自定义 OpenAI 兼容格式
"""

import os
import time
import uuid
import urllib.parse
from typing import Optional, List

import requests

import config
from services.grok_service import get_grok_service
from services.uploader_service import get_uploader_service
from models.image import ImageInfo, ImageType


class ImageService:
    """图片生成服务，支持多种提供商"""

    def __init__(self):
        self.grok_service = get_grok_service()
        self.uploader = get_uploader_service()
        self.provider = config.IMAGE_PROVIDER

    def generate_cover_image(self, title: str, summary: str) -> Optional[ImageInfo]:
        prompt = self.grok_service.generate_cover_prompt(title, summary)
        print(f"封面生成提示词: {prompt}")

        image_info = ImageInfo(
            image_type=ImageType.COVER,
            prompt=prompt
        )

        try:
            url = self._generate_image(prompt, "cover")
            image_info.url = url
            image_info.upload_success = url is not None
            return image_info
        except Exception as e:
            image_info.error_message = str(e)
            return image_info

    def generate_section_images(
        self,
        section_titles: List[str],
        section_contents: List[str]
    ) -> List[ImageInfo]:
        images = []

        for i, (title, content) in enumerate(zip(section_titles, section_contents)):
            prompt = self.grok_service.generate_section_image_prompt(title, content)
            print(f"章节 {i+1} 插图提示词: {prompt}")

            image_info = ImageInfo(
                image_type=ImageType.SECTION,
                prompt=prompt
            )

            try:
                url = self._generate_image(prompt, f"section_{i+1}")
                image_info.url = url
                image_info.upload_success = url is not None
            except Exception as e:
                image_info.error_message = str(e)

            images.append(image_info)
            time.sleep(1)

        return images

    def _generate_image(self, prompt: str, prefix: str) -> Optional[str]:
        """根据配置的提供商生成图片并上传图床"""
        try:
            filename = f"{prefix}_{uuid.uuid4().hex[:8]}.jpg"
            temp_path = os.path.join(config.IMAGES_DIR, filename)

            image_data = self._call_image_api(prompt)

            if not image_data:
                return None

            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(image_data)

            image_url = self.uploader.upload_file(temp_path)

            if os.path.exists(temp_path):
                os.remove(temp_path)

            return image_url

        except Exception as e:
            print(f"图片生成失败: {e}")
            return None

    def _generate_image_url(self, prompt: str) -> Optional[str]:
        """对于返回 URL 的 API（如 DALL-E），直接获取 URL"""
        if self.provider == "openai":
            return self._call_openai_image_url(prompt)
        elif self.provider == "custom":
            return self._call_custom_image_url(prompt)
        return None

    def _call_image_api(self, prompt: str) -> Optional[bytes]:
        """根据提供商调用对应的图片生成 API，返回图片二进制数据"""
        if self.provider == "pollinations":
            return self._call_pollinations(prompt)
        elif self.provider == "openai":
            url = self._call_openai_image_url(prompt)
            if url:
                return self._download_image(url)
            return None
        elif self.provider == "stability":
            return self._call_stability(prompt)
        elif self.provider == "replicate":
            url = self._call_replicate(prompt)
            if url:
                return self._download_image(url)
            return None
        elif self.provider == "custom":
            url = self._call_custom_image_url(prompt)
            if url:
                return self._download_image(url)
            return self._call_custom_image_binary(prompt)
        else:
            raise ValueError(f"不支持的图片生成提供商: {self.provider}")

    def _call_pollinations(self, prompt: str) -> Optional[bytes]:
        """Pollinations.ai 免费图片生成"""
        import urllib3
        urllib3.disable_warnings()

        encoded_prompt = urllib.parse.quote(prompt)
        width = config.POLLINATIONS_WIDTH
        height = config.POLLINATIONS_HEIGHT
        image_url = f"{config.POLLINATIONS_API_URL}{encoded_prompt}?width={width}&height={height}&nologo=true"

        for attempt in range(3):
            try:
                print(f"Pollinations 请求 (尝试 {attempt + 1}/3)...")
                response = requests.get(image_url, timeout=120, verify=False)
                response.raise_for_status()
                if len(response.content) > 1000:
                    return response.content
                print(f"Pollinations 返回数据过小 ({len(response.content)} bytes)，重试...")
            except Exception as e:
                print(f"Pollinations 尝试 {attempt + 1} 失败: {e}")
                if attempt < 2:
                    import time
                    time.sleep(3)

        print("Pollinations 3次尝试均失败")
        return None

    def _call_openai_image_url(self, prompt: str) -> Optional[str]:
        """OpenAI DALL-E 格式图片生成（返回图片 URL）"""
        try:
            headers = {
                "Authorization": f"Bearer {config.IMAGE_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": config.IMAGE_MODEL,
                "prompt": prompt,
                "n": config.IMAGE_N,
                "size": config.IMAGE_SIZE,
                "quality": config.IMAGE_QUALITY,
            }

            print(f"调用 OpenAI 图片生成 API: {config.IMAGE_API_URL}")
            print(f"使用模型: {config.IMAGE_MODEL}")

            response = requests.post(
                config.IMAGE_API_URL,
                json=data,
                headers=headers,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            if "data" in result and len(result["data"]) > 0:
                image_url = result["data"][0].get("url") or result["data"][0].get("b64_json")
                if image_url and image_url.startswith("http"):
                    print(f"OpenAI 图片生成成功: {image_url[:100]}")
                    return image_url
                elif image_url:
                    import base64
                    image_bytes = base64.b64decode(image_url)
                    temp_path = os.path.join(config.IMAGES_DIR, f"oai_{uuid.uuid4().hex[:8]}.png")
                    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(image_bytes)
                    upload_url = self.uploader.upload_file(temp_path)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    return upload_url

            print(f"OpenAI 图片生成响应异常: {result}")
            return None

        except Exception as e:
            print(f"OpenAI 图片生成失败: {e}")
            return None

    def _call_stability(self, prompt: str) -> Optional[bytes]:
        """Stability AI 格式图片生成"""
        try:
            headers = {
                "Authorization": f"Bearer {config.STABILITY_API_KEY}",
                "Accept": "image/*",
            }

            data = {
                "prompt": prompt,
                "output_format": "png",
                "width": config.STABILITY_WIDTH,
                "height": config.STABILITY_HEIGHT,
            }

            if config.STABILITY_MODEL:
                data["model"] = config.STABILITY_MODEL

            print(f"调用 Stability AI 图片生成 API: {config.STABILITY_API_URL}")

            response = requests.post(
                config.STABILITY_API_URL,
                json=data,
                headers=headers,
                timeout=120
            )

            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                if "image" in content_type:
                    return response.content
                else:
                    result = response.json()
                    if "image" in result:
                        import base64
                        return base64.b64decode(result["image"])
                    if "artifacts" in result and len(result["artifacts"]) > 0:
                        import base64
                        return base64.b64decode(result["artifacts"][0]["base64"])

            response.raise_for_status()
            return None

        except Exception as e:
            print(f"Stability AI 图片生成失败: {e}")
            return None

    def _call_replicate(self, prompt: str) -> Optional[str]:
        """Replicate 格式图片生成（异步，需轮询）"""
        try:
            headers = {
                "Authorization": f"Bearer {config.REPLICATE_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "version": config.REPLICATE_MODEL,
                "input": {
                    "prompt": prompt,
                    "width": 1024,
                    "height": 576,
                }
            }

            print(f"调用 Replicate 图片生成 API: {config.REPLICATE_API_URL}")

            response = requests.post(
                config.REPLICATE_API_URL,
                json=data,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            if "urls" in result:
                status_url = result["urls"].get("get", "")
                status = result.get("status", "")

                max_retries = 60
                for _ in range(max_retries):
                    time.sleep(5)
                    poll = requests.get(status_url, headers=headers, timeout=30)
                    poll_result = poll.json()

                    if poll_result.get("status") == "succeeded":
                        output = poll_result.get("output", [])
                        if output:
                            return output[0] if isinstance(output, list) else output
                    elif poll_result.get("status") == "failed":
                        print(f"Replicate 生成失败: {poll_result.get('error')}")
                        return None

                print("Replicate 生成超时")
                return None

            if "output" in result:
                output = result["output"]
                return output[0] if isinstance(output, list) else output

            return None

        except Exception as e:
            print(f"Replicate 图片生成失败: {e}")
            return None

    def _call_custom_image_url(self, prompt: str) -> Optional[str]:
        """自定义 OpenAI 兼容格式图片生成（返回 URL）"""
        try:
            headers = {
                "Authorization": f"Bearer {config.CUSTOM_IMAGE_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": config.CUSTOM_IMAGE_MODEL,
                "prompt": prompt,
                "n": 1,
                "size": config.IMAGE_SIZE,
            }

            print(f"调用自定义图片生成 API: {config.CUSTOM_IMAGE_API_URL}")

            response = requests.post(
                config.CUSTOM_IMAGE_API_URL,
                json=data,
                headers=headers,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            if "data" in result and len(result["data"]) > 0:
                return result["data"][0].get("url")

            return None

        except Exception as e:
            print(f"自定义图片生成失败: {e}")
            return None

    def _call_custom_image_binary(self, prompt: str) -> Optional[bytes]:
        """自定义图片生成 API（直接返回二进制）"""
        try:
            headers = {
                "Authorization": f"Bearer {config.CUSTOM_IMAGE_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": config.CUSTOM_IMAGE_MODEL,
                "prompt": prompt,
            }

            response = requests.post(
                config.CUSTOM_IMAGE_API_URL,
                json=data,
                headers=headers,
                timeout=120
            )

            content_type = response.headers.get("Content-Type", "")
            if "image" in content_type:
                return response.content

            return None

        except Exception as e:
            print(f"自定义图片生成（二进制）失败: {e}")
            return None

    @staticmethod
    def _download_image(url: str) -> Optional[bytes]:
        """下载图片 URL 的二进制数据"""
        try:
            import urllib3
            urllib3.disable_warnings()

            response = requests.get(url, timeout=60, verify=False)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"下载图片失败: {e}")
            return None


_image_service = None


def get_image_service() -> ImageService:
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service
