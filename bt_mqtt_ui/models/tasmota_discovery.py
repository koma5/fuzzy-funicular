from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class MQTTDiscovery(BaseModel):
    ip: str
    dn: str = Field(description="??? name")
    fn: List[Optional[str]]
    hn: str
    mac: str = Field(description="MAC Address")
    md: str
    ty: int
    if_: int = Field(..., alias="if")
    ofln: str
    onln: str
    state: List[str]
    sw: str = Field(description="Firmware version")
    t: str = Field(description="Topic Device identifier")
    ft: str = Field(description="String how topic is constructed")
    tp: List[str] = Field(description="???")
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
