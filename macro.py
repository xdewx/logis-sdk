import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def define_env(env):
    """
    定义宏变量
    """

    @env.macro
    def sdk_version():
        from logis import __version__

        return __version__
