#!/bin/bash

find . -name __pycache__|xargs -I{} rm -r {}

# 清理旧构建
rm -rf dist/ build/ *.egg-info

# 生成发布包
python setup.py sdist bdist_wheel

# 检查包是否符合 PyPI 要求
twine check dist/*

# 发布到 PyPI（需手动执行）
echo "To upload to PyPI, run: twine upload dist/*"
echo "To upload to test PyPI, run: twine upload --repository testpypi dist/*"