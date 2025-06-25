from __future__ import annotations
from collections import deque
from typing import Literal, List, Optional
from dataclasses import dataclass

__all__ = ["Window"]


@dataclass
class Window:
    """滑动窗口对象（内部核心组件）。

    Parameters
    ----------
    _buf : deque[float]
        底层循环缓冲区，`maxlen` 与窗口容量一致。
    _cfg : Window.Config
        窗口配置（类型、时间/计数大小）。
    """

    # ───────────────── Config: 内聚配置结构 ─────────────────
    @dataclass
    class Config:
        """窗口配置结构体。

        Attributes
        ----------
        type : {"time", "count"}
            * ``"time"``  —— 时间窗口，容量 = ``pps * sec + 1``
            * ``"count"`` —— 计数窗口，容量 = ``size``
        sec : int, default ``1``
            时间窗口持续秒数，仅 ``type == "time"`` 时生效。
        size : int, default ``1``
            计数窗口点数，仅 ``type == "count"`` 时生效。
        """

        type: Literal["time", "count"]
        sec: int = 1
        size: int = 1

    # ───────────────── 字段定义 ─────────────────
    _buf: deque[float]
    _cfg: Config

    # ───────────────── 工厂方法 ─────────────────
    @classmethod
    def from_cfg(cls, cfg: Config, pps: int) -> "Window":
        """根据配置创建窗口。

        Parameters
        ----------
        cfg : Window.Config
            窗口配置对象。
        pps : int
            每秒数据点数（points-per-second）。
        """
        size = (max(1, pps * cfg.sec + 1) if cfg.type == "time" else cfg.size)
        return cls(deque(maxlen=size), cfg)

    # ───────────────── 公共接口 ─────────────────
    def push(self, value: float) -> None:
        """向窗口写入新值（自动转换为 ``float``）。"""
        self._buf.append(float(value))

    # -- 便捷只读属性 ------------------------------------
    @property
    def type(self) -> str:
        """窗口类型：``"time"`` 或 ``"count"``。"""
        return self._cfg.type

    def capacity(self) -> Optional[int]:
        """窗口**最大容量**（点数）。``deque.maxlen`` 可能为 ``None``。"""
        return self._buf.maxlen

    def length(self) -> int:
        """当前已填充的数据点数量。"""
        return len(self._buf)

    def is_ready(self) -> bool:
        """窗口是否已填满（用于判断聚合函数是否可用）。"""
        return len(self._buf) == self._buf.maxlen and bool(self._buf)

    def values(self) -> List[float]:
        """以列表形式返回窗口当前全部数据（从旧到新）。"""
        return list(self._buf)

    def reset(self) -> None:
        """清空窗口数据。"""
        self._buf.clear()