"""
图片信息数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class ImageType(Enum):
    """图片类型枚举"""
    COVER = "cover"
    SECTION = "section"
    INLINE = "inline"


@dataclass
class ImageInfo:
    """图片信息实体类"""
    url: Optional[str] = None
    local_path: Optional[str] = None
    image_type: ImageType = ImageType.SECTION
    prompt: str = ""
    generated_at: datetime = field(default_factory=datetime.now)
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    upload_success: bool = False
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'url': self.url,
            'local_path': self.local_path,
            'image_type': self.image_type.value,
            'prompt': self.prompt,
            'upload_success': self.upload_success,
            'error_message': self.error_message,
        }

    @property
    def is_ready(self) -> bool:
        """检查图片是否准备好使用"""
        return self.url is not None and self.upload_success
