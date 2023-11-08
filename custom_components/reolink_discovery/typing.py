"""Reolink Discovery Typings"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, TypedDict
from typing_extensions import NotRequired

from homeassistant.components.dhcp import DhcpServiceInfo
#from typing import Final, Protocol, TypedDict


def _istr(value: any):
    if not value:
        return None
    return str(value).lower()


class ReolinkDiscoveryInfoType(TypedDict):
    """Typed dictionary of prepared info from Reolink discovery"""

    ip: str
    macaddess: str
    hostname: NotRequired[str]
    uuid: NotRequired[str]
    ident: NotRequired[str]

@dataclass(slots=True)
class ReolinkDiscoveryInfo(DhcpServiceInfo):
    """Prepared info from Reolink discovery"""

    uuid: str | None = field(default=None)
    ident: str | None = field(default=None)

    def same_as(self, other: Any):
        """compare to another info object"""

        if isinstance(other, dict):
            _other: ReolinkDiscoveryInfoType = other
            _hash = self.simple_hash(_other["macaddess"], _other.get("uuid"))
        elif not isinstance(other, ReolinkDiscoveryInfo):
            return False
        else:
            _hash = self.simple_hash(other.macaddress, other.uuid)

        return self.simple_hash(self.macaddress, self.uuid) == _hash

    def asdict(self)->ReolinkDiscoveryInfoType:
        """Return as TypedDict"""
        return asdict(self)

    @staticmethod
    def simple_hash(macaddress:str, uuid:str|None=None):
        """simple hash method"""

        if uuid is not None:
            return hash(uuid.lower())
        return hash(macaddress.lower())
