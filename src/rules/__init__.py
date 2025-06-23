# ========================== rules/__init__.py ==========================
"""Minimal‑Stable‑Surface (MSS)

包级仅导出 3 个公开对象：
    * RuleTree   —— 规则树默认实现（Impl）
    * RuleDTO    —— 规则树配置 DTO（Pydantic）
    * SampleDTO  —— 单条监控数据 DTO
其它全部为私有实现 (_window, _unit, _node 等)。
"""

from __future__ import annotations

from .tree import RuleTree                # 默认实现
from ._dto import RuleDTO, SampleDTO    # 数据契约

__all__: list[str] = [
    "RuleTree",
    "RuleDTO",
    "SampleDTO",
]

# 可选工厂：如团队不需要可删除
from pathlib import Path
from typing import Any, Dict


def build_rule_tree(cfg: str | Dict[str, Any] | RuleDTO, *, pps: int) -> "RuleTree":
    """统一构造：接受 JSON 路径/JSON 字符串/dict/Pydantic 实例。"""
    if isinstance(cfg, str) and Path(cfg).is_file():
        cfg = Path(cfg).read_text()
    return RuleTree(cfg, pps=pps)