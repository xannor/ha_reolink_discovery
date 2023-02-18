"""Reolink Discovery Typings"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Protocol, TypedDict
from typing_extensions import NotRequired


def _istr(value: any):
    if not value:
        return None
    return str(value).lower()


@dataclass(frozen=True)
class DiscoveredDevice:
    """Discovered Device"""

    class JSON(TypedDict):
        """JSON"""

        ip: str
        mac: str
        name: NotRequired[str]
        ident: NotRequired[str]
        uuid: NotRequired[str]

    class Keys(Protocol):
        """Keys"""

        ip: Final = "ip"
        mac: Final = "mac"
        name: Final = "name"
        ident: Final = "ident"
        uuid: Final = "uuid"

    ip: str  # pylint: disable=invalid-name
    mac: str
    name: str | None = field(default=None)
    ident: str | None = field(default=None)
    uuid: str | None = field(default=None)

    def __post_init__(self):
        object.__setattr__(self, self.Keys.mac, _istr(self.mac))
        object.__setattr__(self, self.Keys.uuid, _istr(self.uuid))

    def same_as(self, other: DiscoveredDevice | JSON):
        """simple comparison"""
        if isinstance(other, dict):
            return (
                self.uuid is not None and self.uuid == _istr(other.get(self.Keys.uuid, None))
            ) or self.mac == _istr(other.get(self.Keys.mac, None))

        return (self.uuid is not None and self.uuid == other.uuid) or self.mac == other.mac

    def simple_hash(self):
        """hash based off of same_as rules"""
        if self.uuid is not None:
            return hash(self.uuid)
        return hash(self.mac)
