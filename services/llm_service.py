"""
通用 LLM 服务适配层
支持 OpenAI 兼容格式和 Claude 格式
"""

import json
import re
from typing import Dict, List, Optional
import requests

import config


class LLMService:
    """通用大语言模型服务，适配多种 API 格式"""

    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self._setup_provider()

    def _setup_provider(self):
        if self.provider == "openai":
            self.url = config.LLM_API_URL
            self.api_key = config.LLM_API_KEY
            self.model = config.LLM_MODEL
            self.temperature = config.LLM_TEMPERATURE
            self.max_tokens = config.LLM_MAX_TOKENS
            self.top_p = config.LLM_TOP_P
        elif self.provider == "claude":
            self.url = config.CLAUDE_API_URL
            self.api_key = config.CLAUDE_API_KEY
            self.model = config.CLAUDE_MODEL
            self.temperature = config.CLAUDE_TEMPERATURE
            self.max_tokens = config.CLAUDE_MAX_TOKENS
        else:
            raise ValueError(f"不支持的 LLM 提供商: {self.provider}，请选择 openai 或 claude")

    def chat(self, prompt: str, system_prompt: str = None, temperature: float = None) -> str:
        """
        统一聊天接口

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）
            temperature: 温度参数（可选，覆盖默认值）

        Returns:
            AI 回复文本
        """
        if self.provider == "openai":
            return self._chat_openai(prompt, system_prompt, temperature)
        elif self.provider == "claude":
            return self._chat_claude(prompt, system_prompt, temperature)
        else:
            raise ValueError(f"不支持的提供商: {self.provider}")

    def _chat_openai(self, prompt: str, system_prompt: str = None, temperature: float = None) -> str:
        """OpenAI 兼容格式调用（适用于 OpenAI、DeepSeek、Groq、Grok2API、Ollama 等）"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            print(f"正在调用 LLM API ({self.provider}): {self.url}")
            print(f"使用模型: {self.model}")
            response = requests.post(
                self.url,
                json=data,
                headers=headers,
                timeout=120
            )
            print(f"API响应状态: {response.status_code}")

            response_text = response.text
            print(f"响应内容前200字符: {response_text[:200]}")

            if response_text.startswith("data:"):
                print("检测到流式响应，收集所有内容数据块")
                return self._parse_stream_response(response_text)

            response.raise_for_status()

            try:
                result = response.json()["choices"][0]["message"]["content"]
                print(f"API调用成功，返回内容长度: {len(result)}")
                return result
            except (KeyError, TypeError, json.JSONDecodeError) as e:
                print(f"JSON解析错误: {e}")
                return response.text

        except requests.exceptions.RequestException as e:
            print(f"LLM API 调用失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            raise RuntimeError(f"LLM API 调用失败: {e}")

    def _chat_claude(self, prompt: str, system_prompt: str = None, temperature: float = None) -> str:
        """Claude 格式调用（Anthropic Messages API）"""
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": temperature and self.max_tokens or config.CLAUDE_MAX_TOKENS,
            "temperature": temperature or self.temperature,
        }

        if system_prompt:
            data["system"] = system_prompt

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        try:
            print(f"正在调用 Claude API: {self.url}")
            print(f"使用模型: {self.model}")
            response = requests.post(
                self.url,
                json=data,
                headers=headers,
                timeout=120
            )
            print(f"API响应状态: {response.status_code}")

            response_text = response.text
            print(f"响应内容前200字符: {response_text[:200]}")

            if response_text.startswith("data:"):
                print("检测到流式响应，收集所有内容数据块")
                return self._parse_claude_stream_response(response_text)

            response.raise_for_status()

            try:
                result_json = response.json()
                if "content" in result_json and len(result_json["content"]) > 0:
                    content = result_json["content"][0]
                    if content.get("type") == "text":
                        print(f"API调用成功，返回内容长度: {len(content['text'])}")
                        return content["text"]
                if "error" in result_json:
                    raise RuntimeError(f"Claude API 错误: {result_json['error']}")
                raise RuntimeError(f"无法解析 Claude 响应: {result_json}")
            except (KeyError, TypeError, json.JSONDecodeError) as e:
                print(f"JSON解析错误: {e}")
                return response_text

        except requests.exceptions.RequestException as e:
            print(f"Claude API 调用失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            raise RuntimeError(f"Claude API 调用失败: {e}")

    def _parse_stream_response(self, response_text: str) -> str:
        """解析 OpenAI 兼容格式的流式响应"""
        lines = response_text.strip().split('\n')
        content_parts = []

        for line in lines:
            if line.startswith('data: '):
                data_content = line[6:]
                if data_content != "[DONE]":
                    try:
                        json_data = json.loads(data_content)
                        if "choices" in json_data and len(json_data["choices"]) > 0:
                            choice = json_data["choices"][0]
                            if "delta" in choice and "content" in choice["delta"]:
                                content_parts.append(choice["delta"]["content"])
                    except json.JSONDecodeError:
                        pass

        full_content = "".join(content_parts)
        print(f"流式响应处理完成，总内容长度: {len(full_content)}")
        return full_content

    def _parse_claude_stream_response(self, response_text: str) -> str:
        """解析 Claude 流式响应"""
        lines = response_text.strip().split('\n')
        content_parts = []

        for line in lines:
            if line.startswith('data: '):
                data_content = line[6:]
                try:
                    json_data = json.loads(data_content)
                    if json_data.get("type") == "content_block_delta":
                        delta = json_data.get("delta", {})
                        if delta.get("type") == "text_delta":
                            content_parts.append(delta.get("text", ""))
                except json.JSONDecodeError:
                    pass

        full_content = "".join(content_parts)
        print(f"Claude 流式响应处理完成，总内容长度: {len(full_content)}")
        return full_content


_llm_service = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
