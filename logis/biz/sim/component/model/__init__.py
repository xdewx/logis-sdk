import logging
from typing import Any, Dict, Optional

from logis.data_type import TmpId
from logis.util import cast_if_not_none


class ComponentForm:
    """
    entity模块，用来存储交互文件中结点（事件、资源池、货架组等）以及所有空间标记的信息

    TODO:类型标注、泛型
    """

    def __init__(
        self,
        entity_data: Dict[str, Any],
        properties: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__()
        self.type: str = entity_data.get("Type")
        # 实际上是类型id
        self.type_id = self.id = cast_if_not_none(entity_data.get("ID"), str)
        self.type_name: str = entity_data.get("Name", None)
        self.create_edit_id: str = str(entity_data.get("Create_Edit_ID", ""))
        # TODO：这个字段看起来没什么用，考虑去除
        self.agent_id: TmpId = entity_data.get("AgentID")
        # TODO：这个字段还没看到在哪用的
        self.link_ids: Dict[str, Any] = entity_data.get("LinkIDs", {})
        self.extends_dict: Dict[str, Any] = {}
        self.properties: Dict[str, Any] = properties or {}
        self.disabled: bool = entity_data.get("disabled", False)

        if not self.create_edit_id:
            logging.warning(
                f"Warning: Entity {self.type_name} is missing 'Create_Edit_ID'"
            )

    @property
    def name(self) -> Optional[str]:
        return self.properties.get("名称")

    @property
    def display_name(self) -> Optional[str]:
        return self.properties.get("显示名称")
