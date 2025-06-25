from __future__ import annotations
from typing import Callable, Dict, List
import numpy as np

__all__ = ["MetricsKit"]


class MetricsKit:
    """
    统一聚合函数工具类
    --------------------------------------------
    1. 提供常见统计量（平均值、极值、方差等）的静态实现
    2. 通过 `get / all` 方法，暴露「字符串 → 函数」映射
    """

    # ──────────────── ① 聚合函数定义 ────────────────
    @staticmethod
    def mean(vals: List[float]) -> List[float]:
        """算术平均值（保留 2 位小数）"""
        return [round(float(np.mean(vals)), 2)] if vals else []

    @staticmethod
    def vmax(vals: List[float]) -> List[float]:
        """最大值"""
        return [max(vals)] if vals else []

    @staticmethod
    def vmin(vals: List[float]) -> List[float]:
        """最小值"""
        return [min(vals)] if vals else []

    @staticmethod
    def rms(vals: List[float]) -> List[float]:
        """均方根"""
        return [round(float(np.sqrt(np.mean(np.square(vals)))), 2)] if vals else []

    @staticmethod
    def ptp(vals: List[float]) -> List[float]:
        """极差 (peak-to-peak)"""
        return [round(float(np.ptp(vals)), 2)] if vals else []

    @staticmethod
    def rel_var(vals: List[float]) -> List[float]:
        """相对极差 = 极差 / 均值"""
        if not vals:
            return []
        m = np.mean(vals)
        return [0.0] if m == 0 else [round(float(np.ptp(vals) / m), 2)]

    @staticmethod
    def std(vals: List[float]) -> List[float]:
        """标准差"""
        return [round(float(np.std(vals)), 2)] if vals else []

    @staticmethod
    def var(vals: List[float]) -> List[float]:
        """方差"""
        return [round(float(np.var(vals)), 2)] if vals else []

    @staticmethod
    def slope(vals: List[float]) -> List[float]:
        """
        线性斜率：用一阶多项式拟合序列 (x, y)，返回 k
        若点不足两枚，则视作平坦，返回 0
        """
        if len(vals) < 2:
            return [0.0]
        x = np.arange(len(vals))
        y = np.array(vals, dtype=float)
        slope, _ = np.polyfit(x, y, 1)
        return [round(float(slope), 2)]

    # ──────────────── ② 字符串 → 函数映射 ────────────────
    # 注意：必须取 .__func__，否则得到的是不可调用的 `staticmethod` 对象
    _AGG_MAP: Dict[str, Callable[[List[float]], List[float]]] = {
        # 平均值（别名 avg）
        "mean": mean.__func__, # type: ignore
        "avg": mean.__func__, # type: ignore

        # 极大/极小
        "vmax": vmax.__func__, # type: ignore
        "max": vmax.__func__, # type: ignore
        "vmin": vmin.__func__, # type: ignore
        "min": vmin.__func__, # type: ignore

        # 其他统计量
        "rms": rms.__func__, # type: ignore
        "ptp": ptp.__func__, # type: ignore
        "rel_var": rel_var.__func__, # type: ignore
        "std": std.__func__, # type: ignore
        "var": var.__func__, # type: ignore
        "slope": slope.__func__, # type: ignore
    }

    # ──────────────── ③ 对外接口 ────────────────
    @classmethod
    def get(cls, agg: str) -> Callable[[List[float]], List[float]]:
        """
        通过名字获取聚合函数；若不存在，返回占位函数（始终返回空列表）
        """
        return cls._AGG_MAP.get(agg, lambda _: [])

    @classmethod
    def all(cls) -> Dict[str, Callable[[List[float]], List[float]]]:
        """返回映射表的浅拷贝，可一次性注入到其他模块"""
        return cls._AGG_MAP.copy()
