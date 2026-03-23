import pandas
from ipa.decorator import deprecated


def is_prop_value_invalid(v: str):
    return pandas.isna(v) or (not v)


def is_stock_name_invalid(name: str):
    """
    判断是否是非法的货物名称
    """
    return is_prop_value_invalid(name)


@deprecated("no need to use static class")
class StockUtil:

    @staticmethod
    def is_prop_value_invalid(v: str):
        return is_prop_value_invalid(v)

    @staticmethod
    def is_stock_name_invalid(name: str):
        return is_stock_name_invalid(name)
