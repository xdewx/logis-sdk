from datetime import datetime

import pandas as pd
from dateutil.parser import parse


def parse_datetime(date_str: str):
    """
    主要增加了对中文日期的解析
    """
    if not date_str:  # 处理空值
        return None

    if isinstance(date_str, (datetime)):
        return date_str

    if isinstance(date_str, (pd.Timestamp)):
        return date_str.to_pydatetime()

    format = [
        "%Y年%m月%d日 %H:%M:%S",  # 年月日格式
        "%Y年%m月%d日",  # 年月日格式（仅日期）
    ]
    for f in format:
        try:
            return datetime.strptime(date_str, f)
        except ValueError:
            continue
    return parse(date_str)
