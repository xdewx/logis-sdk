# logis-sdk

络捷斯特 Python 模块合集

## 安装

```bash
pip install logis-sdk
```

默认只安装核心依赖（约 10MB），按需选择额外功能：

### 按子模块安装

```bash
# 路径规划
pip install 'logis-sdk[alg]'

# 业务仿真
pip install 'logis-sdk[biz]'

# 数据类型支持
pip install 'logis-sdk[data_type]'

# 数学工具
pip install 'logis-sdk[math]'

# 监控指标
pip install 'logis-sdk[metric]'

# 消息队列
pip install 'logis-sdk[mq]'

# 仿真引擎
pip install 'logis-sdk[simpy]'

# 任务调度
pip install 'logis-sdk[task]'

# Web 工具（FastAPI 等）
pip install 'logis-sdk[util]'

# AI 大模型（OpenAI、智谱）
pip install 'logis-sdk[ai]'

# 图表
pip install 'logis-sdk[charts]'

# 架构图
pip install 'logis-sdk[diagrams]'
```

### 按功能组合安装

```bash
# 仿真全栈（biz + simpy + alg + task）
pip install 'logis-sdk[simulation]'

# 数据处理（data_type + math + metric）
pip install 'logis-sdk[data]'

# 可视化（charts + diagrams）
pip install 'logis-sdk[viz]'

# Web 服务
pip install 'logis-sdk[web]'

# 消息通信
pip install 'logis-sdk[messaging]'
```

### 全部安装

```bash
pip install 'logis-sdk[all]'
```

### 开发者

```bash
# 完整环境（含测试/构建工具）
pip install -e '.[dev]'
# 或
pip install -r requirements.txt
```

## 使用示例

```python
from logis.alg.path_finding import Finder

class MyPathFinder(Finder):
    """
    基于pathfinding模块实现自定义寻路算法
    """
    pass

```

```python
from logis.alg.path_finding import PathFindingAlgorithm,PathFindingInput,PathFindingOutput

class MyPathFindingAlgorithm(PathFindingAlgorithm):
    """
    基于自定义输入输出实现具体寻路算法
    """
    def find_path(self, input: PathFindingInput) -> PathFindingOutput:
        # 实现具体的寻路算法
        pass
```

## 贡献指南

参见 [CONTRIBUTING.md](./CONTRIBUTING.md)
