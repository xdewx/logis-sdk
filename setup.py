from setuptools import find_packages, setup

from logis import __version__

BASE = "requirements"


def _read(filename):
    path = f"{BASE}/{filename}"
    with open(path, "r", encoding="utf-8") as f:
        lines = []
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            lines.append(line.split(" ")[0])
        return lines


install_requires = _read("core.txt")

extras_require = {
    "alg": _read("optional/alg.txt"),
    "biz": _read("optional/biz.txt"),
    "math": _read("optional/math.txt"),
    "metric": _read("optional/metric.txt"),
    "mq": _read("optional/mq.txt"),
    "simpy": _read("optional/simpy.txt"),
    "web": _read("optional/web.txt"),
    "ai": _read("optional/ai.txt"),
    "viz": _read("optional/viz.txt"),
    "dev": _read("dev.txt"),
}

# 功能分组（组合多个子模块）
extras_require["simulation"] = list(
    set(
        _read("optional/biz.txt")
        + _read("optional/simpy.txt")
        + _read("optional/alg.txt")
    )
)
extras_require["data"] = list(
    set(_read("optional/math.txt") + _read("optional/metric.txt"))
)
extras_require["messaging"] = _read("optional/mq.txt")
extras_require["ai"] = _read("optional/ai.txt")

# "all" = 所有子模块可选依赖
_MODULE_KEYS = {
    "alg",
    "biz",
    "math",
    "metric",
    "mq",
    "simpy",
    "web",
    "ai",
    "viz",
}
extras_require["all"] = list(set().union(*(extras_require[k] for k in _MODULE_KEYS)))

setup(
    name="logis-sdk",
    version=__version__,
    description="络捷斯特 Python 模块合集",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="leoking",
    author_email="present150608@sina.com",
    packages=find_packages(),
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires=">=3.8",
)
