# ========================= rules/tree.py ============================
"""RuleTree ‑ 公开实现（Impl）"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Any

from ._dto import RuleDTO, SampleDTO
from .src.rules._internal._node import _Node

__all__: list[str] = ["RuleTree"]


class RuleTree:
    """Stable Impl · 满足 SRP + 可静态类型检查"""

    # ---- construction --------------------------------------------------
    def __init__(self, cfg: str | Dict[str, Any] | RuleDTO, *, pps: int):
        self._cfg: RuleDTO = self._validate_cfg(cfg)
        self._pps = pps
        self._root: _Node = _Node(self._cfg, pps=pps)

        self._metrics: List[str] = self._collect_metrics()
        self._active_path: List[str] = []
        self._reached_leaf: bool = False
        self._last_node_info: Dict[str, Any] = {}

        self._reorder_tree()

    # factory – keep __init__ light                                        
    @classmethod
    def from_cfg(cls, cfg: str | Dict[str, Any] | RuleDTO, *, pps: int) -> "RuleTree":
        return cls(cfg, pps=pps)

    # ---- public API ----------------------------------------------------
    def push(self, sample: SampleDTO | Dict[str, float]) -> None:
        dto = sample if isinstance(sample, SampleDTO) else SampleDTO.model_validate(sample)
        self._root.push_recursive(dto.model_dump())
        self._update_active_path()

    def reset(self) -> None:
        self._root.reset()

    # ---- read‑only props ----------------------------------------------
    @property
    def metrics(self) -> List[str]:
        return self._metrics

    @property
    def active_path(self) -> List[str]:
        return self._active_path

    @property
    def reached_leaf(self) -> bool:
        return self._reached_leaf

    @property
    def last_node_info(self) -> Dict[str, Any]:
        return self._last_node_info

    # ---- internal helpers ---------------------------------------------
    @staticmethod
    def _validate_cfg(raw: str | Dict[str, Any] | RuleDTO) -> RuleDTO:
        if isinstance(raw, RuleDTO):
            return raw
        if isinstance(raw, str):
            # try file path else JSON string
            path = Path(raw)
            content = path.read_text() if path.is_file() else raw
            return RuleDTO.model_validate_json(content)
        return RuleDTO.model_validate(raw)

    def _collect_metrics(self) -> List[str]:
        mets: set[str] = set()

        def walk(node: _Node) -> None:
            if not node.is_always_true:
                mets.update(u.metric for u in node.units)
            for s in node.subs:
                walk(s)

        walk(self._root)
        return sorted(mets)

    def _reorder_tree(self) -> None:
        stack: List[tuple[_Node, bool]] = [(self._root, False)]
        while stack:
            node, visited = stack.pop()
            if not visited:
                stack.append((node, True))
                stack.extend((s, False) for s in node.subs)
            else:
                node.subs.sort(key=lambda n: n.is_always_true)

    def _update_active_path(self) -> None:
        self._active_path.clear()
        self._reached_leaf = False
        self._last_node_info = {}

        stack: List[tuple[_Node, List[str]]] = [(self._root, [self._root
