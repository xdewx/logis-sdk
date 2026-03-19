from typing import List, Optional

from pydantic import BaseModel, Field


class ComponentConfigItem(BaseModel):
    """
    组件配置项，用于前端展示和后端处理
    """

    # 中文名
    label: Optional[str] = None
    # 描述
    description: Optional[str] = None
    # 类型编码
    type_id: str
    # 加载器，用于指导后端解析组件
    loader: Optional[str] = None
    # 是否卸载，用于卸载已加载的组件
    unload: bool = False

    # 是否启用配置
    enabled: bool = True


class ComponentConfig(BaseModel):
    """
    组件配置
    """

    entity_list: List[ComponentConfigItem] = Field(default_factory=list)
