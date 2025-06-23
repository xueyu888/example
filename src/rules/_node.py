# ========================= rules/_node.py ============================
"""私有树节点实现"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, cast

from ._dto import RuleDTO, UnitDTO          # ⚠️ 依赖 pydantic 定义
from ._unit import Unit                       # 你刚贴的 Unit 实现


__all__ = ["Node"]


@dataclass
class Node:
    """递归规则节点：封装子节点、Unit 判定与活动状态"""

    # ----------- 结构字段（由 dataclass 直接持有） ------------------
    id: str
    is_always_true: bool
    units: List[Unit]
    subs: List["Node"]
    is_leaf: bool

    # 派生字段（init=False → 构造后由工厂方法补充）
    sub_ids: List[str] = field(init=False)
    units_info: List[Dict[str, object]] = field(init=False)
    _eval_cache: List[Optional[bool]] = field(init=False)
    _match_cache: List[Dict[str, Optional[bool]]] = field(init=False)

    # ----------- 工厂方法 ------------------------------------------
    @classmethod
    def from_cfg(cls, cfg: RuleDTO, pps: int) -> "Node":
        """由 RuleDTO + pps 构建 Node"""
        is_always_true = cfg.units in ("else", "root")

        # Unit 构建
        if is_always_true:
            units: List[Unit] = []
        else:
            unit_cfgs = cast(List[UnitDTO], cfg.units)  # 静态类型收窄
            units = [Unit.from_cfg(u, pps=pps) for u in unit_cfgs]

        # 子节点递归
        subs = [cls.from_cfg(s, pps) for s in (cfg.sub or [])]

        # 实例化
        node = cls(
            id=cfg.id,
            is_always_true=is_always_true,
            units=units,
            subs=subs,
            is_leaf=not subs,
        )

        # ------- 派生字段填充 -------
        node.sub_ids = [s.id for s in subs]
        node.units_info = [
            {"metric": u._metric, "window": u._win}  # 仅示例，两字段够用
            for u in units
        ]
        return node

    # ---------------- runtime API ----------------
    def push(self, sample: Dict[str, float]) -> None:
        """向本节点及所有子节点推送一条样本"""
        if not self.is_always_true:
            for u in self.units:
                u.push(sample)
            self._refresh_cache()

        for s in self.subs:
            s.push(sample)

    def _refresh_cache(self) -> None:
        """重新计算本节点单位判定结果缓存"""
        self._eval_cache = [u.is_valid() for u in self.units]
        self._match_cache = [{u._metric: r} for u, r in zip(self.units, self._eval_cache)]

    # ---------------- 状态查询 --------------------
    @property
    def is_active(self) -> Optional[bool]:
        """True/False/None = 全 True / 有 False / 有 None"""
        if self.is_always_true:
            return True
        if False in self._eval_cache:
            return False
        return None if None in self._eval_cache else True

    @property
    def units_result(self) -> List[Dict[str, Optional[bool]]]:
        """每个 Unit 的判定结果缓存"""
        return self._match_cache

    # ---------------- 维护方法 --------------------
    def reset(self) -> None:
        """递归重置本节点及子节点"""
        for u in self.units:
            u.reset()
        for s in self.subs:
            s.reset()
        self._eval_cache.clear()
        self._match_cache.clear()
