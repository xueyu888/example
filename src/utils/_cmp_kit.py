# src/utils/cmp_kit.py

from typing import Callable, Dict
from loguru import logger

__all__ = ["CmpKit"]

class CmpKit:
    """
    区间比较函数工具类。
    提供对不同区间类型（如 "[]", "[)", "(]" 等）的判断函数获取。
    """

    _cmp_map: Dict[str, Callable[[float, float, float], bool]] = {
        "[]": lambda x, a, b: a <= x <= b,
        "[)": lambda x, a, b: a <= x < b,
        "(]": lambda x, a, b: a < x <= b,
        "()": lambda x, a, b: a < x < b,
    }

    @staticmethod
    def get(cmp_type: str) -> Callable[[float, float, float], bool]:
        """
        获取指定区间类型的比较函数。
        不支持的类型将返回恒为 False 的函数，并记录错误日志。

        示例:
            CmpKit.get("[]")(5, 3, 7) → True
        """
        if cmp_type not in CmpKit._cmp_map:
            logger.error(f"Unsupported comparison type: {cmp_type}")
            return lambda x, a, b: False
        return CmpKit._cmp_map[cmp_type]
