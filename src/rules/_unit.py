from __future__ import annotations
from typing import Callable, List, Optional, Tuple
from dataclasses import dataclass
from ..utils._metrics_kit import MetricsKit
from ..utils._cmp_kit import CmpKit
from ._window import Window

__all__ = ["Unit"]

@dataclass
class Unit:
    
    @classmethod
    def create( cls, 
                win: Window, 
                agg: str, 
                cmp: dict[str, Tuple[float, float]],
                cmp_values: Tuple[float, float] = (0.0, 0.0)
                ) -> "Unit":
    

        # 1) 聚合函数（none → None）
        agg_fn: Optional[Callable[[List[float]], List[float]]] = (
            None if agg == "none" else MetricsKit.get(agg)
        )

        # 2) 区间比较函数
        cmp_fn = CmpKit.get(cmp)

        # 3) 返回实例
        return cls(win, agg_fn, cmp_fn, cmp_values)

    # ──────────────────── 公共接口 ────────────────────
    def push_and_check(self, value: float) -> Optional[bool]:
        """写入新值到窗口"""
        self._win.push(value)

        """窗口聚合后判定是否命中"""
        if self._agg_fn is None:
            return False
        
        vals = self._agg_fn(self._win.values())
        
        return bool(vals) and self._cmp_fn(vals[0], self._cmp_values[0], self._cmp_values[1])

    def reset(self) -> None:
        """清空窗口历史数据"""
        self._win.reset()

    # ──────────────────── 私有成员变量 ────────────────────
    _win: Window
    _agg_fn: Optional[Callable[[List[float]], List[float]]]
    _cmp_fn: Callable[[float, float, float], bool]
    _cmp_values: Tuple[float, float] 