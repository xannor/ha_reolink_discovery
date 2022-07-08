"""Reolink Discovery Component"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
import logging

from homeassistant.core import HomeAssistant, CALLBACK_TYPE
from homeassistant import config_entries
from homeassistant.components.network import async_get_ipv4_broadcast_addresses
from homeassistant.util import dt
from homeassistant.helpers.event import async_track_time_interval

from homeassistant.const import CONF_SCAN_INTERVAL

from .typing import DiscoveredDevice as BaseDiscoveredDevice

from .discovery import DiscoveryProtocol, async_listen, async_ping

from .const import CONF_BROADCAST, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


def async_get_poll_interval(config_entry: config_entries.ConfigEntry):
    """Get the poll interval"""
    interval = config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    return timedelta(seconds=interval)


class _Ping:
    def __init__(self, hass: HomeAssistant, entry: config_entries.ConfigEntry) -> None:
        self._interval: timedelta = None
        self._broadcast: list[str] = None
        self._cleanup: CALLBACK_TYPE = None
        hass.create_task(self._update(hass, entry))
        entry.async_on_unload(entry.add_update_listener(self._update))

    async def _ping(self, *_):
        for addr in self._broadcast:
            async_ping(addr)

    async def _update(self, hass: HomeAssistant, entry: config_entries.ConfigEntry):
        addr = entry.options.get(CONF_BROADCAST, None)

        if addr and (not self._broadcast or self._broadcast[0] != addr):
            self._broadcast = [addr]
        elif not addr or not self._broadcast:
            self._broadcast = list(
                (str(addr) for addr in await async_get_ipv4_broadcast_addresses(hass))
            )
        interval = async_get_poll_interval(entry)
        if interval != self._interval:
            if self._cleanup:
                self._cleanup()
            self._interval = interval
            self._cleanup = async_track_time_interval(hass, self._ping, self._interval)
            entry.async_on_unload(self._cleanup)
            await self._ping()


async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    """Setup ReoLink Discovery Component"""

    _LOGGER.debug("Setting up reolink discovery component")

    (transport, _) = await async_listen(__type=_Discoverer, logger=_LOGGER, hass=hass)
    entry.async_on_unload(transport.close)

    _Ping(hass, entry)

    return True


async def async_remove_entry(hass: HomeAssistant, _: config_entries.ConfigEntry):
    """Remove entry"""

    hass.data.popitem(DOMAIN, None)


@dataclass
class DiscoveredDevice:
    """Discovered Device with discovery information"""

    device: BaseDiscoveredDevice
    first_seen: datetime = field(default_factory=dt.utcnow)
    last_update: datetime = field(default_factory=dt.utcnow)
    last_seen: datetime = field(default_factory=dt.utcnow)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, DiscoveredDevice):
            return self.device.same_as(__o.device)
        return self.device.same_as(__o)

    def __hash__(self):
        return self.device.simple_hash()


class _Discoverer(DiscoveryProtocol):
    def __init__(self, *, hass: HomeAssistant, **kwargs) -> None:
        super().__init__(**kwargs)
        self.hass = hass

    def discovered_device(self, device: BaseDiscoveredDevice) -> None:
        super().discovered_device(device)
        data = asdict(device)
        self.hass.bus.async_fire(DOMAIN, data)
