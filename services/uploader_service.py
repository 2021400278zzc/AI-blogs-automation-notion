"""
图床上传服务
支持 tc.741568.xyz 图床
"""

import os
import uuid
import requests
from typing import Optional

import config


class UploaderService:
    """图床上传服务"""

    def __init__(self):
        self.upload_url = config.IMAGE_UPLOAD_URL
        self.params = config.IMAGE_UPLOAD_PARAMS

    def upload_file(self, file_path: str) -> Optional[str]:
        """
        上传本地图片文件到图床

        Args:
            file_path: 本地图片文件路径

        Returns:
            上传成功返回图片 URL，失败返回 None
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                import urllib3
                urllib3.disable_warnings()
                response = requests.post(
                    self.upload_url,
                    params=self.params,
                    files=files,
                    timeout=60,
                    verify=False
                )
            response.raise_for_status()
            result = response.json()
            print(f"图床响应: {result}")

            if isinstance(result, list) and len(result) > 0:
                item = result[0] if isinstance(result[0], dict) else {}
                url = item.get("src") or item.get("url") or (result[0] if isinstance(result[0], str) else None)
            elif isinstance(result, dict):
                if result.get("code") == 200 or result.get("status") == "success" or "data" in result:
                    data = result.get("data", result.get("url"))
                    if isinstance(data, list) and len(data) > 0:
                        item = data[0] if isinstance(data[0], dict) else {}
                        url = item.get("url") or (data[0] if isinstance(data[0], str) else None)
                    elif isinstance(data, dict):
                        url = data.get("url")
                    elif isinstance(data, str):
                        url = data
                    else:
                        url = result.get("url")
                else:
                    raise RuntimeError(f"上传失败: {result.get('message', '未知错误')}")
            else:
                url = None

            if url and not url.startswith("http"):
                url = f"https://tc.741568.xyz{url}"
            if url:
                print(f"图片上传成功: {url}")
                return url
            raise RuntimeError(f"上传失败，无法解析响应: {result}")

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"上传请求失败: {e}")
        except Exception as e:
            raise RuntimeError(f"上传过程出错: {e}")

    def upload_from_url(self, image_url: str, temp_filename: str = None) -> Optional[str]:
        """
        从 URL 下载图片并上传到图床

        Args:
            image_url: 图片 URL
            temp_filename: 临时文件名

        Returns:
            上传成功返回图床 URL，失败返回 None
        """
        try:
            # 下载图片
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            image_data = response.content

            # 确定文件扩展名
            content_type = response.headers.get("Content-Type", "")
            if "png" in content_type:
                ext = ".png"
            elif "jpg" in content_type or "jpeg" in content_type:
                ext = ".jpg"
            elif "webp" in content_type:
                ext = ".webp"
            else:
                ext = ".jpg"

            # 保存临时文件
            if temp_filename is None:
                temp_filename = str(uuid.uuid4())[:8]

            temp_path = os.path.join(config.IMAGES_DIR, f"{temp_filename}{ext}")
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)

            with open(temp_path, "wb") as f:
                f.write(image_data)

            # 上传图床
            result_url = self.upload_file(temp_path)

            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return result_url

        except Exception as e:
            raise RuntimeError(f"从 URL 上传图片失败: {e}")

    def upload_bytes(self, image_data: bytes, filename: str) -> Optional[str]:
        """
        直接上传图片字节数据

        Args:
            image_data: 图片二进制数据
            filename: 文件名

        Returns:
            上传成功返回图片 URL
        """
        try:
            temp_path = os.path.join(config.IMAGES_DIR, filename)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)

            with open(temp_path, "wb") as f:
                f.write(image_data)

            result_url = self.upload_file(temp_path)

            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return result_url

        except Exception as e:
            raise RuntimeError(f"上传字节数据失败: {e}")


# 单例实例
_uploader_service = None


def get_uploader_service() -> UploaderService:
    """获取 UploaderService 单例"""
    global _uploader_service
    if _uploader_service is None:
        _uploader_service = UploaderService()
    return _uploader_service
