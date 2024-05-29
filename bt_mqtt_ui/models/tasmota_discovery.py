from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class MQTTDiscovery(BaseModel):
    ip: str
    dn: str = Field(description="Device name")
    fn: List[Optional[str]] = Field(description="Friendly name(s)")
    hn: str = Field(description="Host name")
    mac: str = Field(description="MAC Address")
    md: str = Field(description="Module type, e.g. Generic")
    ty: int
    if_: int = Field(..., alias="if")
    ofln: str = Field(description="Last will message sent by broker on offline")
    onln: str = Field(
        description="Last will message that overwrites the offline message for broker"
    )
    state: List[str] = Field(description="Capabilities")
    sw: str = Field(description="Firmware version")
    t: str = Field(description="Topic Device identifier")
    ft: str = Field(description="String how topic is constructed")
    tp: List[str] = Field(
        description="tele: Data messages, cmnd: topic to publish commands to device, stat: topic for state changes"
    )
    rl: List[int]
    swc: List[int]
    swn: List[None]
    btn: List[int]
    so: Dict[str, int]
    lk: int
    lt_st: int
    bat: int
    dslp: int
    sho: List
    sht: List
    ver: int
