from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class PlatformInfo(BaseModel):
    signature: Optional[str] = None
    url: str


class VersionInfo(BaseModel):
    version: str  # 版本号，必选字符串
    notes: str  # 更新说明，必选字符串
    pub_date: datetime  # 发布时间，自动解析ISO 8601格式（如2026-02-02T10:00:00Z）
    platforms: Dict[str, PlatformInfo]


class UpdateResponse(BaseModel):
    current_version: str
    version_info: VersionInfo
    need_update: bool
