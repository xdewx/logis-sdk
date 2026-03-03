from setuptools import find_packages, setup

from logis import __version__

install_requires = []
with open("requirements.txt", "r") as f:
    install_requires = f.readlines()
    install_requires = [x.strip() for x in install_requires if x]
install_requires = list(filter(lambda x: not x.startswith("#"), install_requires))

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
    python_requires=">=3.8",
)
