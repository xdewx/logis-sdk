!!! info "解释说明"
    仿真大师内置很多蓝图，例如进入、搬运、退出、生产等等，每个蓝图都有自己预置的逻辑，如果您发现现有蓝图无法满足您的需求，您可以自定义蓝图并替换掉原有蓝图。


### 操作步骤

1. 打开`$HOME\AppData\Local\logis\smart_simulation\conf`目录，修改`component_config.json`文件，添加你的蓝图定义
2. 稍等片刻等到系统热加载完成
3. 重新开始仿真，观察您的蓝图是否生效

其中`component_config.json`文件的格式如下：

```json
{
  "$schema": "https://gist.githubusercontent.com/xdewx/c4276bc08b2dd03672f9bd475108f584/raw/48a026405c8280703d24c945ab0219a9adcc193b/logis-simulation-component-config.json",
  "entity_list": [
    {
      "type_id": "40022", // 蓝图类型ID
      "label": "My GoodsToPerson", // 蓝图名称
      "description": "重写GoodsToPerson组件", // 蓝图描述
      "unload": true, // 是否卸载蓝图，用于想要还原原蓝图的场景
      "loader": "hmlib.loader.MyLoader", // 自定义加载器用于定位您的蓝图实现类
      "enabled": true // 是否启用此配置
    }
  ]
}

```

自定义蓝图示例：

```python
from src.blueprint import GoodsToPerson


class MyGoodsToPerson(GoodsToPerson):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log.info("MyGoodsToPerson initialized")

```

`loader`示例：

```python
from typing import Type

from logis.biz.sim import ComponentLoader
from logis.biz.sim.component import ComponentForm as Entity
from logis.biz.sim.data_type import ComponentConfigItem
from logis.biz.sim.iface.component import IComponent


class MyLoader(ComponentLoader):

    def load(self, item: ComponentConfigItem) -> Type[IComponent]:
        if item.type_id in ["40017", "40022"]:
            return MyGoodsToPerson
        raise NotImplementedError("load method not implemented")

```
