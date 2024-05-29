from datetime import datetime

from pydantic import BaseModel, Field


class Wifi(BaseModel):
    AP: int
    SSId: str
    BSSId: str
    Channel: int
    Mode: str
    RSSI: int
    Signal: int
    LinkCount: int
    Downtime: str = Field(description="Example: 0T00:17:11")


class DeviceState(BaseModel):
    Time: datetime
    Uptime: str = Field(description="Example: 0T00:17:11")
    UptimeSec: int
    Heap: int
    SleepMode: str = Field(description="Example: Dynamic")
    Sleep: int
    LoadAvg: int
    MqttCount: int
    POWER: str | None = Field(description="Example: OFF")
    Wifi: Wifi
