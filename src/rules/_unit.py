# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Callable, Dict, List, Optional
import math
from dataclasses import dataclass

from ..utils.metrics_kit import MetricsKit
from ._dto import UnitDTO
from ._window import Window


__all__ = ["Unit"]

@dataclass
class Unit:
    _metric: str
    _win: Window
    _agg_fn: Optional[Callable[[List[float]], List[float]]]
    _cmp_fn: Callable[[float, float, float], bool]          
    _lower: float
    _upper: float

    @classmethod
    def from_cfg(cls, cfg: UnitDTO, pps: int) -> "Unit":
        win_len: int = max(1, pps * cfg.window.sec + 1) if cfg.window.type == "time" else cfg.window.size
        _win = Window.from_cfg(win_len)
        _agg_fn = MetricsKit.get_aggs().get(cfg.agg) if cfg.agg != "none" else None
        _cmp_fn = MetricsKit.get_cmps()[cfg.cmp.type]
        return cls(cfg.metric, _win, _agg_fn, _cmp_fn, *cfg.cmp.value)

    # ---- runtime API ---------------------------------------------------
    def push(self, sample: Dict[str, float]) -> None:
        self._win.push(sample[self._metric])

    def is_valid(self) -> Optional[bool]:
        if not self._win.ready() or any(math.isnan(v) for v in self._win.values()):
            return None

        values = self._win.values()
        aggregated = self._agg_fn(values) if self._agg_fn else values  # List[float]

        return all(self._cmp_fn(v, self._lower, self._upper) for v in aggregated)

    def reset(self) -> None:
        self._win.reset()
