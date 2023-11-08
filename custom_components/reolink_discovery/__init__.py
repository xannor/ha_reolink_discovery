"""Reolink Discovery Component"""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant, CALLBACK_TYPE
from homeassistant import config_entries
from homeassistant.components.network import async_get_ipv4_broadcast_addresses
from homeassistant.helpers.discovery import discover
from homeassistant.helpers.discovery_flow import async_create_flow
from homeassistant.helpers.event import async_track_time_interval

from homeassistant.const import CONF_SCAN_INTERVAL

from .typing import ReolinkDiscoveryInfo

from .core import ReolinkDiscoveryProtocol

from .const import (
    CONF_BROADCAST,
    CONF_COMPONENT,
    DEFAULT_INTEGRATION,
    DEFAULT_SCAN_INTERVAL,
    DHCP_INTEGRATIONS,
    DOMAIN,
    SUPPORTED_INTEGRATIONS,
)

_LOGGER = logging.getLogger(__name__)


def async_get_poll_interval(config_entry: config_entries.ConfigEntry):
    """Get the poll interval"""
    interval = config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    return timedelta(seconds=interval)


async def async_setup(hass: HomeAssistant, config: config_entries.ConfigType) -> bool:
    """Setup ReoLink Discovery Component"""

    hass.data[DOMAIN] = config

    return True


async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    """Setup ReoLink Discovery Component Entry"""
    _LOGGER.debug("Setting up reolink discovery component")
    hass_config = hass.data.get(DOMAIN)

    def _discovered(device:ReolinkDiscoveryInfo):
        component: str = entry.options.get(CONF_COMPONENT, DEFAULT_INTEGRATION)
        if component in SUPPORTED_INTEGRATIONS:
            async_create_flow(hass, component, {"source": config_entries.SOURCE_INTEGRATION_DISCOVERY, "provider": DOMAIN}, device)
        elif component in DHCP_INTEGRATIONS:
            async_create_flow(hass, component, {"source": config_entries.SOURCE_DHCP, "provider": DOMAIN}, device)
        else:
            discover(hass, DOMAIN, device.asdict(), component, hass_config)

    (transport, discovery) = await ReolinkDiscoveryProtocol.async_create_listener(_discovered, logger=_LOGGER)

    broadcast:list[str] = []
    interval = timedelta()
    time_cleanup: CALLBACK_TYPE = None

    def _ping(*_):
        for addr in broadcast:
            discovery.async_ping(addr)

    async def _update(hass: HomeAssistant, entry: config_entries.ConfigEntry):
        nonlocal broadcast, interval, time_cleanup

        addr = entry.options.get(CONF_BROADCAST, None)

        if addr and (not broadcast or broadcast[0] != addr):
            broadcast = [addr]
        elif not addr or not broadcast:
            broadcast = list(
                (str(addr) for addr in await async_get_ipv4_broadcast_addresses(hass))
            )
        poll = async_get_poll_interval(entry)
        if interval != poll:
            if time_cleanup:
                time_cleanup()
            interval = poll
            time_cleanup = async_track_time_interval(hass, _ping, interval)
            _ping()

    update_cleanup = entry.add_update_listener(_update)

    def _unload():
        nonlocal transport, update_cleanup
        if transport:
            transport.close()
        transport = None
        if time_cleanup:
            time_cleanup()
        time_cleanup = None
        if update_cleanup:
            update_cleanup()
        update_cleanup = None

    entry.async_on_unload(_unload)

    await _update(hass, entry)

    return True

# async def async_remove_entry(hass: HomeAssistant, _: config_entries.ConfigEntry):
#     """Remove entry"""
