"""Reolink Discovery Constants"""

from typing import Final


DOMAIN: Final = "reolink_discovery"

DEFAULT_SCAN_INTERVAL: Final = 30

CONF_BROADCAST: Final = "broadcast_addr"
CONF_COMPONENT: Final = "notify_component"

SUPPORTED_INTEGRATIONS: Final = ["reolink", "reolink_rest"]
