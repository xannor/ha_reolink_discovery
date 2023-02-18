"""Reolink Discovery Configuration"""

import ipaddress
import voluptuous as vol

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import callback
from homeassistant.components.network import async_get_ipv4_broadcast_addresses

from homeassistant.const import CONF_SCAN_INTERVAL

from .const import CONF_BROADCAST, CONF_COMPONENT, DEFAULT_SCAN_INTERVAL, DOMAIN

_NETWORKS: list[
    ipaddress.IPv4Network
] = (
    ipaddress.IPv4Address._constants._private_networks  # pylint: disable=protected-access
)


class ReolinkDiscoveryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ReoLink Discovery"""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> data_entry_flow.FlowResult:
        self._async_abort_entries_match()

        return self.async_create_entry(title="Reolink Device Discovery", data={})

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return ReolinkDiscoveryOptionsFlow(config_entry)


class ReolinkDiscoveryOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow for ReoLink Discovery"""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, any] | None = None
    ) -> data_entry_flow.FlowResult:
        """init"""

        errors = {}
        if user_input:
            if CONF_BROADCAST in user_input:
                try:
                    addr = ipaddress.ip_interface(user_input[CONF_BROADCAST])
                    if not isinstance(addr, ipaddress.IPv4Interface):
                        net = None
                        errors[CONF_BROADCAST] = "invalid-address"
                    elif not addr.is_private:
                        errors[CONF_BROADCAST] = "public-address"
                        net = None
                    elif addr.network.prefixlen == 32:
                        net = next((n for n in _NETWORKS if addr in n), None)
                        # try not to go outside of a /24 when no mask provided
                        if net.prefixlen < 24:
                            net = next(
                                s for s in net.subnets(new_prefix=24) if addr in s
                            )
                    else:
                        net = addr.network
                except ValueError:
                    errors[CONF_BROADCAST] = "invalid-address"
                    net = None

                if net:
                    user_input[CONF_BROADCAST] = str(net.broadcast_address)

            if not errors:
                return self.async_create_entry(title="", data=user_input)
        else:
            user_input = self.config_entry.options

        addr = str(next(iter(await async_get_ipv4_broadcast_addresses(self.hass)), ""))

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        description={
                            "suggested_value": user_input.get(
                                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                            )
                        },
                    ): vol.All(vol.Coerce(int), vol.Range(min=1)),
                    vol.Optional(
                        CONF_BROADCAST,
                        description={
                            "suggested_value": user_input.get(CONF_BROADCAST, addr)
                        },
                    ): vol.All(vol.Coerce(str), vol.Length(min=7, max=16)),
                    vol.Optional(
                        CONF_COMPONENT,
                        description={
                            "suggested_value": user_input.get(
                                CONF_COMPONENT, vol.UNDEFINED
                            )
                        },
                    ): str,
                }
            ),
            errors=errors,
        )
