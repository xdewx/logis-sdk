__doc__ = """
配置模块
包含一些全局配置
"""


import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class IAppConfig(ABC):
    """
    应用配置接口
    """

    @abstractmethod
    def get_runtime_root_dir(self, *args, **kwargs) -> Optional[Path]:
        pass

    def get_root_dir(self, *args, **kwargs) -> Optional[Path]:
        """
        此方法只是一个别名，返回与get_runtime_root_dir相同的结果
        """
        return self.get_runtime_root_dir(*args, **kwargs)

    # @abstractmethod
    # def get_user_data_root_dir(self, *args, **kwargs) -> Optional[Path]:
    #     pass

    @abstractmethod
    def get_logs_dir(self, *args, **kwargs) -> Optional[Path]:
        pass

    @abstractmethod
    def get_config_dir(self, *args, **kwargs) -> Optional[Path]:
        pass

    @abstractmethod
    def get_data_dir(self, *args, **kwargs) -> Optional[Path]:
        pass

    def get_temp_dir(self, *args, **kwargs) -> Optional[Path]:
        raise NotImplementedError()

    def get_middleware_dir(self, *args, **kwargs) -> Optional[Path]:
        raise NotImplementedError()

    def get_extension_dir(self, *args, **kwargs) -> Optional[Path]:
        raise NotImplementedError()

    def get_app_logger(self, *args, **kwargs) -> logging.Logger:
        raise NotImplementedError()

    def get_sidecar_dir(self, *args, **kwargs) -> Optional[Path]:
        raise NotImplementedError()
