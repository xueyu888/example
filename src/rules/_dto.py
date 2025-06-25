# ========================== rules/models.py ============================
"""Pydantic 数据契约与 DTO 定义：
- RuleDTO: 表示规则树的结构
- SampleDTO: 表示一次样本输入（包含指标）
- WindowDTO: 表示窗口配置
- CmpDTO: 表示区间判断配置
"""

from __future__ import annotations
from typing import Literal, Tuple, List
from pydantic import BaseModel, Field, ConfigDict

__all__: list[str] = [
    "RuleDTO",
    "SampleDTO",
    "UnitDTO",
    "WindowDTO",
    "CmpDTO",
]


# ---------------- 单元规则 DTO ------------------------------------------
class UnitDTO(BaseModel):
    """
    单个规则单元的配置结构：
    - metric: 指标名称，如 "angle"
    - window: 滑动窗口配置
    - agg: 聚合方法，如 avg, min, max, sum, none
    - cmp: 区间比较配置（区间类型和范围）
    """
    metric: str
    window: WindowDTO
    agg: Literal["avg", "min", "max", "sum", "none"]
    cmp: CmpDTO

    model_config = ConfigDict(extra="forbid")  # 禁止出现未定义字段


# ---------------- 规则树结构 -------------------------------------------
class RuleDTO(BaseModel):
    """
    规则树节点结构：
    - id: 节点标识
    - units: 该节点包含的判断单元（为空表示逻辑组合节点）
    - sub: 子规则节点列表（可嵌套）
    """
    id: str
    units: List[UnitDTO] | Literal["else", "root"] | None = None
    sub: List["RuleDTO"] | None = None

    model_config = ConfigDict(extra="forbid")


# ---------------- 样本数据输入 DTO -------------------------------------
class SampleDTO(BaseModel):
    """
    单条输入样本：
    - ts: 时间戳（必须字段）
    - 其他字段表示任意指标数据（动态扩展）
    """
    ts: int = Field(..., ge=0)

    model_config = ConfigDict(extra="allow")  # 允许附加指标字段（动态）


# ---------------- 窗口配置结构体 ---------------------------------------
class WindowDTO(BaseModel):
    """
    滑动窗口配置：
    - type: "time" 表示时间窗口（单位秒），"count" 表示固定点数
    - sec: 若为时间窗口，表示持续秒数（最小为 1）
    - size: 若为点数窗口，表示数据点数量（最小为 1）
    """
    type: Literal["time", "count"]
    sec: int = Field(1, ge=1)
    size: int = Field(1, ge=1)

    model_config = ConfigDict(extra="forbid")


# ---------------- 区间配置结构体 ---------------------------------------
class CmpDTO(BaseModel):
    """
    区间比较配置：
    - type: 区间类型，如 [], (), [), (]
    - value: 区间上下界（左闭右闭等）
    """
    type: Literal["()", "[]", "[)", "(]"]
    value: Tuple[float, float]

    model_config = ConfigDict(extra="forbid")
