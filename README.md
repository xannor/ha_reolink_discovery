# Reolink Device Discovery for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]


[![Community Forum][forum-shield]][forum]

This "helper" component will implement the ReoLink Device discovery protocol, broadcasting to the local network a request for
reolink devices to identify themselves. For every device that replies, the information is relayed into Home Assistant via a local event.

This component is HACS compatible and only has a dependency on the existance of the network component (should be in a standard setup)

This does require the ability to send a broadcast package to the network and the ability to receive a reply. Because of the type of packet there are some limitations, or additional work that may need to be done, depending on your setup.

This component only relays an event, it provides no functionallity for handling/managing discovered devices, that is left to separate components. This is so other compoments can take advantage of discovery without needing a hard coded reference or library.

[Developer Info](./developer.md)

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `reolink_discovery`.
4. Download _all_ the files from the `custom_components/reolink_discovery/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Reolink Discovery"

## Configuration is done in the UI

The default is to send a UDP (port 2000) request to the local network broadcast range of the install and await a UDP reply on port 3000. If your setup is behind a firewall, or is in a separate network (for example a custom docker setup) you may need to add 3000/udp to the forwarded ports.

Once the integration is installed it should be operating, to see it you can use the developer tools panel and listen for event reolink_discovery, it should occur about every 30 seconds by default.

The two configurable options are the interval and the broadcast address.

Interval lets you adjust how often it will send a request.

Broadcast address is to handle setups where the network that Home Assistant sees, is not the actual local network, in here you can provide a new IP address to broadcast to. For example, if you are running this in a devcontainer, you will not see any results because broadcast packets are not forwarded by default, if you change this to your computers ip address, you should start to see replies.

[Developer info](./developer.md)

<!---->

***

[reolink_discovery]: https://github.com/xannor/ha_reolink_discovery
[commits-shield]: https://img.shields.io/github/commit-activity/y/xannor/ha_reolink_discovery.svg?style=for-the-badge
[commits]: https://github.com/xannor/ha_reolink_discovery/commits/master
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license]: https://github.com/xannor/ha_reolink_discovery/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/xannor/ha_reolink_discovery.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Xannor%20%40xannor-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/xannor/ha_reolink_discovery.svg?style=for-the-badge
[releases]: https://github.com/xannor/ha_reolink_discovery/releases
[user_profile]: https://github.com/xannor

