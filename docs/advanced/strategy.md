## 智能体调度策略

```python

from logis.biz.sim.agent import IAgentSelectionStrategy, IAgent, IAgentPool


class AlwaysTheFirstAgent(IAgentSelectionStrategy):

    def select_agent(self, agent_pool: IAgentPool, **kwargs) -> IAgent:
        agent_pool = agent_pool or self.agent_pool
        raise NotImplementedError()

```

## 智能体空闲策略


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
        logging.warning(
            "RandomRackSelectionStrategy.select_racks is working",
        )
        racks = super().select_racks(operation, stock, rack_group, **kwargs)
        # 这里以一种打乱的方式返回货架，也即是随机选择货架
        random.shuffle(racks)
        return racks

```