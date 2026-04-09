import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def sdk_version():
    try:
        from logis import __version__

        return __version__
    except:
        return None


def define_env(env):
    """
    定义宏变量
    """

    env.variables["root"] = str(project_root)

    @env.macro
    def sdk_install_name():
        v = sdk_version()
        v = "==" + v if v else ""
        return f"logis-sdk{v}"
