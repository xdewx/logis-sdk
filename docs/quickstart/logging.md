
## 默认日志

```python
import logging
import logging.config
from logis.logging import get_default_dict_config_builder

dict_config = get_default_dict_config_builder().build()
print(dict_config)
logging.config.dictConfig(dict_config)
log = logging.getLogger("app")
log.info("这是一条 info 日志")
log.warning("这是一条 warning 日志")
log.error("这是一条 error 日志")

```

## 日志构造器

```python
import logging
from logis.logging import LoggerBuilder

logger = LoggerBuilder()
    .level(logging.INFO) # 设置日志级别
    .build()
logger.info("这是一条 info 日志")
logger.warning("这是一条 warning 日志")
logger.error("这是一条 error 日志")

```