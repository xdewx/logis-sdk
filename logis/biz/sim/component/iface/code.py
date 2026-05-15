from typing import Optional, Type, TypeVar

from logis.biz.sim.iface import IBlueprint

C = TypeVar("C")


class ICodeBlueprint(IBlueprint):
    """
    代码蓝图组件的抽象基类
    """

    def instantiate_strategy(
        self, strategy_type: Type[C], index: int = -1, **kwargs
    ) -> Optional[C]:
        """
        实例化策略

        Args:
            strategy_type (Type[C]): 策略的父类
            index (int, optional): 策略的索引。默认值为-1。
            kwargs (dict): 其他参数

        Returns:
            Optional[C]: 策略实例，如果成功实例化策略，否则返回None

        Raises:
            NotImplementedError: 如果不支持实例化策略
        """
        raise NotImplementedError("instantiate_strategy 未实现")
