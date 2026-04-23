## 智能体调度策略

!!! info "解释说明"
    当有搬运任务需要执行时，需要从资源池中选择一个智能体来执行任务

    开发者通过实现 `IAgentSelectionStrategy` 接口，来定义自己的智能体选择策略。


```python

from logis.biz.sim.agent import IAgentSelectionStrategy, IAgent, IAgentPool


class AlwaysTheFirstAgent(IAgentSelectionStrategy):

    def select_agent(self, agent_pool: IAgentPool, **kwargs) -> IAgent:
        agent_pool = agent_pool or self.agent_pool
        raise NotImplementedError()

```

## 智能体空闲策略

!!! info "解释说明"
    当智能体完成一次搬运任务后，需要确定是停留在原地、还是回到初始位置、亦或是其他。

    开发者通过实现 `AgentIdleStrategy` 接口，来定义自己的空闲策略。


```python

import random
from typing import Any, Callable, Generator

from simpy.events import Event

from logis.biz.sim.agent import AgentClass, AgentIdleStrategy
from logis.biz.sim.agent.iface.base import Any, Generator
from logis.biz.sim.component import IGrid


class FindFreePoint(AgentIdleStrategy):
    """
    当空闲时移动至任意一个空闲点
    """
    def on_idle(
        self,
        agent: AgentClass | None = None,
        is_idle: Callable[[AgentClass], bool] | None = None,
        **kwargs
    ) -> Generator[Event, Any, None]:
        agent = agent or self.agent
        is_idle = is_idle or self.is_idle
        if not is_idle(agent):
            yield self.ctx.get_env().timeout(0)
            return
        graph = agent.resolve_binding_graph()
        assert isinstance(graph, IGrid), "暂不支持非网格图"
        free_points = graph.get_free_points()
        yield from agent.move(random.choice(free_points))

```

## 货架选择策略

!!! info "解释说明"
    搬运设备前往货架组取货、放货时，需要确定应该操作具体哪个货架、哪个储位、以什么顺序操作。

    开发者通过实现 `IRackSelectionStrategy` 接口，来定义自己的货架选择策略。


```python

import logging
import random
from typing import List

from logis.biz.sim.const import OperationType
from logis.biz.sim.stock.model import IStock
from logis.biz.sim.storage import IRackSelectionStrategy, RackGroupClass
from logis.biz.sim.storage.iface.device import IRack


class RandomRackSelectionStrategy(IRackSelectionStrategy):
    """
    随机货架选择策略
    """

    def select_racks(
        self,
        operation: OperationType,
        stock: IStock,
        rack_group: RackGroupClass | None = None,
        **kwargs
    ) -> List[IRack]:
        assert self.ctx is not None, "ctx is None"
        # 下面一行只是为了能在控制台看到相关日志输出，以便于说明此策略正常执行了
        logging.warning(
            "RandomRackSelectionStrategy.select_racks is working",
        )
        # 父类方法中会根据操作类型、货物类型返回符合条件的货架列表，但具体操作货架的顺序开发者可以自定义
        racks = super().select_racks(operation, stock, rack_group, **kwargs)
        # 这里以一种打乱的方式返回货架，也即是随机选择货架
        random.shuffle(racks)
        return racks

```