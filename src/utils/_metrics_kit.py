from __future__ import annotations
from typing import Callable, Dict, List
import math
import numpy as np

__all__ = ["MetricsKit"]


class MetricsKit:
    """
    统一聚合函数工具类
    1. 提供常见统计量（平均值、极值、方差等）
    2. 通过 `get / all / has` 暴露「字符串 → 函数」映射
    """

    _NAN = float("nan")  # 空数据兜底

    # ────────── ① 聚合函数定义：全部改为 float ──────────
    @staticmethod
    def mean(vals: List[float]) -> float:
        return round(float(np.mean(vals)), 2) if vals else MetricsKit._NAN

    @staticmethod
    def vmax(vals: List[float]) -> float:
        return max(vals) if vals else MetricsKit._NAN

    @staticmethod
    def vmin(vals: List[float]) -> float:
        return min(vals) if vals else MetricsKit._NAN

    @staticmethod
    def rms(vals: List[float]) -> float:
        return round(float(np.sqrt(np.mean(np.square(vals)))), 2) if vals else MetricsKit._NAN

    @staticmethod
    def ptp(vals: List[float]) -> float:
        return round(float(np.ptp(vals)), 2) if vals else MetricsKit._NAN

    @staticmethod
    def rel_var(vals: List[float]) -> float:
        if not vals:
            return MetricsKit._NAN
        m = np.mean(vals)
        return 0.0 if math.isclose(m, 0.0) else round(float(np.ptp(vals) / m), 2)

    @staticmethod
    def std(vals: List[float]) -> float:
        return round(float(np.std(vals)), 2) if vals else MetricsKit._NAN

    @staticmethod
    def var(vals: List[float]) -> float:
        return round(float(np.var(vals)), 2) if vals else MetricsKit._NAN

    @staticmethod
    def slope(vals: List[float]) -> float:
        if len(vals) < 2:
            return 0.0
        x = np.arange(len(vals))
        y = np.array(vals, dtype=float)
        k, _ = np.polyfit(x, y, 1)
        return round(float(k), 2)

    # ────────── ② 字符串 → 函数映射 ──────────
    _AGG_MAP: Dict[str, Callable[[List[float]], float]] = {
        "mean": mean.__func__, "avg": mean.__func__, # type: ignore
        "vmax": vmax.__func__, "max": vmax.__func__, # type: ignore
        "vmin": vmin.__func__, "min": vmin.__func__, # type: ignore
        "rms": rms.__func__, # type: ignore
        "ptp": ptp.__func__, # type: ignore
        "rel_var": rel_var.__func__, # type: ignore
        "std": std.__func__, # type: ignore
        "var": var.__func__, # type: ignore
        "slope": slope.__func__, # type: ignore
    }

    # ────────── ③ 对外接口 ──────────
    @classmethod
    def get(cls, agg: str) -> Callable[[List[float]], float]:
        """根据名称获取聚合函数；若不存在返回恒 `nan` 占位函数"""
        return cls._AGG_MAP.get(agg, lambda _vals: MetricsKit._NAN)

    @classmethod
    def has(cls, agg: str) -> bool:
        return agg in cls._AGG_MAP

    @classmethod
    def all(cls) -> Dict[str, Callable[[List[float]], float]]:
        return cls._AGG_MAP.copy()
