# ========================= rules/_window.py ===========================
"""私有滑动窗口实现 —— 不在 MSS 暴露"""

from collections import deque
from typing import List
from dataclasses import dataclass


__all__: list[str] = []  # 不暴露

@dataclass
class Window: 
    _buf: deque[float]
    """Fixed‑size float deque with helpers."""

    @classmethod
    def from_cfg(cls, size: int) -> "Window":
        return cls(deque(maxlen=size))

    # ---------------- public ----------------
    def push(self, value: float) -> None:
        self._buf.append(float(value))

    def ready(self) -> bool:
        return len(self._buf) == self._buf.maxlen and bool(self._buf)

    def values(self) -> List[float]:
        return list(self._buf)

    def reset(self) -> None:
        self._buf.clear()
