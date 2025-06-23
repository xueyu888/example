# src/utils/metrics_kit.py

from __future__ import annotations
from typing import List
import numpy as np

__all__ = ["MetricsKit"]

class MetricsKit:
    """
    提供统一聚合函数和区间比较函数的工具类。
    """

    # ---------------- 聚合函数定义 ----------------
    @staticmethod
    def mean(vals: List[float]) -> List[float]:
        return [round(float(np.mean(vals)), 2)] if vals else []

    @staticmethod
    def vmax(vals: List[float]) -> List[float]:
        return [max(vals)] if vals else []

    @staticmethod
    def vmin(vals: List[float]) -> List[float]:
        return [min(vals)] if vals else []

    @staticmethod
    def rms(vals: List[float]) -> List[float]:
        return [round(float(np.sqrt(np.mean(np.square(vals)))), 2)] if vals else []

    @staticmethod
    def ptp(vals: List[float]) -> List[float]:
        return [round(float(np.ptp(vals)), 2)] if vals else []

    @staticmethod
    def rel_var(vals: List[float]) -> List[float]:
        if not vals:
            return []
        m = np.mean(vals)
        return [0.0] if m == 0 else [round(float(np.ptp(vals) / m), 2)]

    @staticmethod
    def std(vals: List[float]) -> List[float]:
        return [round(float(np.std(vals)), 2)] if vals else []

    @staticmethod
    def var(vals: List[float]) -> List[float]:
        return [round(float(np.var(vals)), 2)] if vals else []

    @staticmethod
    def slope(vals: List[float]) -> List[float]:
        if len(vals) < 2:
            return [0.0]
        x = np.arange(len(vals))
        y = np.array(vals, dtype=float)
        slope, _ = np.polyfit(x, y, 1)
        return [round(float(slope), 2)]


