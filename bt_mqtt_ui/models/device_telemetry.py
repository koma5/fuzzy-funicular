from datetime import datetime
from pydantic import BaseModel, Field


class ENERGY(BaseModel):
    """Entry for devices that measure current"""
    TotalStartTime: datetime
    Total: float
    Yesterday: int
    Today: int
    Period: int
    Power: float
    ApparentPower: float
    ReactivePower: float
    Factor: int
    Voltage: float
    Current: float


class DeviceTelemetry(BaseModel):
    Time: datetime = Field(description="Example: 2024-05-20T13:36:54")
    energy: ENERGY | None = Field(None, alias="ENERGY")
