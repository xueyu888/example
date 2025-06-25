from typing import Callable, Dict, cast, ClassVar
from loguru import logger
from dataclasses import dataclass


__all__ = ["CmpKit"]


class CmpKit:
    """
    区间比较函数工具类
    --------------------------------------------
    1. 提供对不同区间类型（如 "[]", "[)", "(]" 等）的静态比较函数
    2. 通过 `get / all` 方法，暴露「字符串 → 函数」映射
    """

    # ──────────────── ① 比较函数定义 ────────────────
    @staticmethod
    def closed(x: float, a: float, b: float) -> bool:
        """闭区间 [a, b]"""
        return a <= x <= b

    @staticmethod
    def left_closed(x: float, a: float, b: float) -> bool:
        """左闭右开区间 [a, b)"""
        return a <= x < b

    @staticmethod
    def right_closed(x: float, a: float, b: float) -> bool:
        """左开右闭区间 (a, b]"""
        return a < x <= b

    @staticmethod
    def open(x: float, a: float, b: float) -> bool:
        """开区间 (a, b)"""
        return a < x < b

    # ──────────────── ② 字符串 → 函数映射 ────────────────
    # 注意：必须取 .__func__，否则得到的是不可调用的 `staticmethod` 对象
    _CMP_MAP: Dict[str, Callable[[float, float, float], bool]] = {
        "[]": closed.__func__,         # type: ignore
        "[)": left_closed.__func__,   # type: ignore
        "(]": right_closed.__func__,  # type: ignore
        "()": open.__func__,          # type: ignore
    }

    # ──────────────── ③ 对外接口 ────────────────
    @classmethod
    def get(cls, cmp_type: str) -> Callable[[float, float, float], bool]:
        """
        获取指定区间类型的比较函数。
        若不支持该类型，则返回恒为 False 的占位函数，并记录错误日志。
        """
        if cmp_type not in cls._CMP_MAP:
            logger.error(f"Unsupported comparison type: {cmp_type}")
            return cast(Callable[[float, float, float], bool], lambda *_: False)
        return cls._CMP_MAP[cmp_type]

    @classmethod
    def all(cls) -> Dict[str, Callable[[float, float, float], bool]]:
        """返回比较函数映射表的浅拷贝"""
        return cls._CMP_MAP.copy()

@dataclass
class Cmp:
    @classmethod
    def create(cls,
               cmp_kit: type[CmpKit],
               cmp_values: tuple[float, float]
    ) -> "Cmp":
        """
        创建一个 Cmp 实例，包含比较函数和比较值。
        """
        return cls(cmp_values)

    _cmp_values: tuple[float, float]
    _cmp_kit: type[CmpKit] = CmpKit

