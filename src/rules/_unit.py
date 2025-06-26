from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple, Type

from ..utils._metrics_kit import MetricsKit
from ..utils._cmp_kit import CmpKit
from ._window import Window

__all__ = ["Unit"]

def _always_true(*_: float) -> bool:
    """默认比较函数：永远返回 True。"""
    return True


@dataclass
class Unit:
    """滑动窗口 + 聚合 + 比较的一体化单元。"""
    @classmethod
    def create(
        cls,
        win: Window,
        agg: str,
        cmp_kit: Type[CmpKit],
        cmp_type: str,
        cmp_bounds: Tuple[float, float] = (0.0, 0.0),
    ) -> "Unit":
        """
        Parameters
        ----------
        win : Window
            滑动窗口
        agg : str
            聚合类型标识符（或 'none'）
        cmp_kit : Type[CmpKit]
            比较工具箱类
        cmp_type : str
            比较函数名
        cmp_bounds : Tuple[float, float]
            比较上下界 (lower, upper)
        """
        # ---------------- 参数校验集中处理 ----------------
        errors: List[str] = []

        if agg != "none" and not MetricsKit.has(agg):   
            errors.append(f"Unknown aggregation type: {agg}")

        if cmp_type and not cmp_kit.has(cmp_type):     
            errors.append(f"Unknown comparison type: {cmp_type}")

        if cmp_bounds[0] > cmp_bounds[1]:
            errors.append(f"Invalid cmp_bounds: {cmp_bounds}, must be (lower <= upper)")

        if errors:
            raise ValueError("Invalid Unit configuration:\n" + "\n".join(errors))

        # ---------------- 函数解析 ----------------
        agg_fn = None if agg == "none" else MetricsKit.get(agg)
        cmp_fn = cmp_kit.get(cmp_type) if cmp_type else _always_true

        return cls(win, agg_fn, cmp_fn, cmp_bounds)

    # -------- 主执行逻辑 --------
    def push_and_check(self, value: float) -> bool:
        """写入数据并立即判断是否命中比较条件。"""
        self._win.push(value)

        if not self._win.is_ready():
            return False

        if self._agg_fn is None:
            raise ValueError("Aggregation function is not set. Use 'none' for no aggregation.")

        vals = self._agg_fn(self._win.values())
        if not vals:
            return False

        lower, upper = self._cmp_bounds
        return self._cmp_fn(vals, lower, upper)

    def reset(self) -> None:
        """清空窗口历史数据。"""
        self._win.reset()

    # -------- 数据字段 --------
    _win: Window
    _agg_fn: Optional[Callable[[List[float]], float]]
    _cmp_fn: Callable[[float, float, float], bool]
    _cmp_bounds: Tuple[float, float]
