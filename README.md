# logis-sdk

络捷斯特 Python 模块合集

## 安装

```bash
pip install logis-sdk
```

## 使用示例

```python
from logis.alg.pathfinding import PathFindingAlgorithm,PathFindingInput,PathFindingOutput

class MyPathFindingAlgorithm(PathFindingAlgorithm):
    def find_path(self, input: PathFindingInput) -> PathFindingOutput:
        # 实现具体的寻路算法
        pass

```

## 贡献指南

欢迎提交 Pull Request 或报告问题。