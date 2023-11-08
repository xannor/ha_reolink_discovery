"""Reolink Discovery Constants"""

from typing import Final


DOMAIN: Final = "reolink_discovery"

DEFAULT_SCAN_INTERVAL: Final = 30

CONF_BROADCAST: Final = "broadcast_addr"
CONF_COMPONENT: Final = "notify_component"

DEFAULT_INTEGRATION: Final = "reolink"
SUPPORTED_INTEGRATIONS: Final = []
DHCP_INTEGRATIONS: Final = [DEFAULT_INTEGRATION]