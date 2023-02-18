"""Reolink Discovery Component"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant, CALLBACK_TYPE, Event, callback
from homeassistant import config_entries
from homeassistant.components.network import async_get_ipv4_broadcast_addresses
from homeassistant.util import dt
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.loader import async_get_custom_components

if TYPE_CHECKING:
    from homeassistant.helpers import (
        discovery as helper_discovery,
        discovery_flow as helper_discovery_flow,
    )
from ._utilities.hass_typing import hass_bound

from homeassistant.const import CONF_SCAN_INTERVAL

from .typing import DiscoveredDevice

from .discovery import DiscoveryProtocol, async_listen, async_ping

from .const import (
    CONF_BROADCAST,
    CONF_COMPONENT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SUPPORTED_INTEGRATIONS,
)

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

    async def refresh(self):
        """Refresh discovery"""
        await self._ping()

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


async def async_setup(hass: HomeAssistant, config: config_entries.ConfigType) -> bool:
    """Setup ReoLink Discovery Component"""

    hass.data[DOMAIN] = config

    return True


async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    """Setup ReoLink Discovery Component Entry"""
    _LOGGER.debug("Setting up reolink discovery component")
    hass_config = hass.data.get(DOMAIN)

    components = list(
        domain
        for domain in await async_get_custom_components(hass)
        if domain in SUPPORTED_INTEGRATIONS
    )
    if CONF_COMPONENT not in entry.options and len(components) == 1:
        options = entry.options.copy()
        options[CONF_COMPONENT] = components[0]
        hass.config_entries.async_update_entry(entry, options=options)

    (transport, _) = await async_listen(
        __type=_Discoverer, logger=_LOGGER, hass=hass, hass_config=hass_config
    )
    entry.async_on_unload(transport.close)

    pinger = _Ping(hass, entry)

    return True


# async def async_remove_entry(hass: HomeAssistant, _: config_entries.ConfigEntry):
#     """Remove entry"""


class _Discoverer(DiscoveryProtocol):
    def __init__(
        self, *, hass: HomeAssistant, hass_config: config_entries.ConfigType, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.hass = hass
        self._hass_config = hass_config
        self.config_entry: config_entries.ConfigEntry = (
            config_entries.current_entry.get()
        )

    def discovered_device(self, device: DiscoveredDevice) -> None:
        super().discovered_device(device)
        data = asdict(device)
        component: str = self.config_entry.options.get(CONF_COMPONENT, None)
        discovery: helper_discovery = self.hass.helpers.discovery
        hass_bound(discovery.discover)(DOMAIN, data, component, self._hass_config)
        discovery_flow: helper_discovery_flow = self.hass.helpers.discovery_flow
        hass_bound(discovery_flow.async_create_flow)(
            component,
            {"source": config_entries.SOURCE_DISCOVERY, "provider": DOMAIN},
            data,
        )
