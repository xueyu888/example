# ========================= rules/_node.py ============================

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List

from ._unit import Unit
from ._dto import RuleDTO  

__all__ = ["Node"]


# --------------------------------------------------------------------
#                           数 据 结 构
# --------------------------------------------------------------------
@dataclass
class Node:
    """规则树节点：持有 Unit 判定与递归子节点"""

    # —— 基础字段（由 dataclass 直接持有） ——
    node_id: str
    is_unconditional: bool
    units: List[Unit]
    subs: List["Node"]
    is_leaf: bool

    # —— 派生字段（init=False，构造结束后由工厂补全） ——
    sub_ids: List[str] = field(init=False)
    units_metrics: List[str] = field(init=False)           # 仅保存 metric 字符串
    units_info: List[Dict[str, object]] = field(init=False)

    # —— 运行期缓存 ——
    _eval_cache: List[bool] = field(init=False)
    _match_cache: List[Dict[str, bool]] = field(init=False)

    # ----------------------------------------------------------------
    #                        构  造  工  厂
    # ----------------------------------------------------------------
    @classmethod
    def from_cfg(cls, cfg: RuleDTO, *, pps: int) -> "Node":
        """根据 RuleDTO + pps 递归构建 Node"""
        is_always = cfg.units in ("else", "root")

        # Units
        units: List[Unit] = []
        if not is_always:
            # cfg.units 在严格模式下已是 List[UnitDTO]
            units = [Unit.from_cfg(u, pps) for u in cfg.units]  # type: ignore[arg-type]

        # 子节点
        subs = [cls.from_cfg(c, pps=pps) for c in (cfg.sub or [])]

        # 实例
        node = cls(
            node_id = cfg.id,
            is_unconditional = is_always,
            units = units,
            subs = subs,
            is_leaf = not subs,
        )

        # —— 派生属性 ——  
        node.sub_ids = [s.node_id for s in subs]
        node.units_metrics = [u.get_info().metric for u in units]
        node.units_info = [u.get_info().__dict__ for u in units]

        return node

    # ----------------------------------------------------------------
    #                        运  行  时  接  口
    # ----------------------------------------------------------------
    def push(self, sample: Dict[str, float]) -> None:
        """
        将一条样本同时推送给本节点与所有子节点。
        `sample` 形如 {"speed": 12.3, "angle": 2.1}
        """
        if not self.is_unconditional:
            # 将样本映射到各 Unit 所需的 metric
            for u, metric in zip(self.units, self.units_metrics):
                value = sample.get(metric, math.nan)
                u.push(value)
            self._refresh_cache()

        # 向子树传播
        for sub in self.subs:
            sub.push(sample)

    def _refresh_cache(self) -> None:
        """刷新本节点判定缓存"""
        self._eval_cache = [u.check() for u in self.units]
        self._match_cache = [
            {metric: res} for metric, res in zip(self.units_metrics, self._eval_cache)
        ]

    # ----------------------------------------------------------------
    #                        状  态  查  询
    # ----------------------------------------------------------------
    @property
    def is_active(self) -> bool:
        """
        如果节点为 always_true → True；否则所有 Unit.check() 均为 True 方返回 True。
        """
        return True if self.is_unconditional else all(self._eval_cache)

    @property
    def units_results(self) -> List[Dict[str, bool]]:
        """返回形如 [{'speed': True}, {'angle': False}] 的 Unit 判定结果列表"""
        return self._match_cache

    # ----------------------------------------------------------------
    #                        维  护  接  口
    # ----------------------------------------------------------------
    def reset(self) -> None:
        """递归重置本节点及全部子节点"""
        for u in self.units:
            u.reset()
        for s in self.subs:
            s.reset()
        self._eval_cache.clear()
        self._match_cache.clear()
