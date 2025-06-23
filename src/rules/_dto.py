
# ========================== rules/models.py ============================
"""Pydantic 数据契约 & DTO"""

from __future__ import annotations

from typing import Literal, Tuple, List
from pydantic import BaseModel, Field, ConfigDict

__all__: list[str] = [
    "RuleDTO",
    "SampleDTO",
]

class UnitDTO(BaseModel):
    metric: str
    window: _WindowDTO
    agg: Literal["avg", "min", "max", "sum", "none"]
    cmp: _CmpDTO

    model_config = ConfigDict(extra="forbid")

# ---------------- Rule‑tree Config DTO -------------------------------
class RuleDTO(BaseModel):
    id: str
    units: List[UnitDTO] | Literal["else", "root"] | None = None
    sub: List["RuleDTO"] | None = None

    model_config = ConfigDict(extra="forbid")


# ---------------- Sample DTO -----------------------------------------
class SampleDTO(BaseModel):
    """贫血数据模型（DTO）：必须包含时间戳，可带任意指标。"""

    _ts: int = Field(..., ge=0)

    model_config = ConfigDict(extra="allow")  # 动态指标字段


# ---------------- Window / Interval / Unit Config ---------------------
class _WindowDTO(BaseModel):
    type: Literal["time", "count"]

    sec: int = Field(1, ge=1)
    size: int = Field(1, ge=1)

    model_config = ConfigDict(extra="forbid")



class _CmpDTO(BaseModel):
    type: Literal["open", "closed", "left_closed", "right_closed"]
    value: Tuple[float, float]

    model_config = ConfigDict(extra="forbid")





