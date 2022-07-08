Reolink Device Discovery for Home Assistant

This "helper" component will implement the ReoLink Device discovery protocol, broadcasting to the local network a request for
reolink devices to identify themselves. For every device that replies, the information is relayed into Home Assistant via a local event.

This component is HACS compatible and only has a dependency on the existance of the network component (should be in a standard setup)

This does require the ability to send a broadcast package to the network and the ability to receive a reply. Because of the type of packet there are some limitations, or additional work that may need to be done, depending on your setup.

The default is to send a UDP (port 2000) request to the local network broadcast range of the install and await a UDP reply on port 3000. If your setup is behind a firewall, or is in a separate network (for example a custom docker setup) you may need to add 3000/udp to the forwarded ports.

Once the intefration is installed it should be operating, to see it you can use the developer tools panel and listen for event reolink_discovery, it should occur about every 30 seconds by default.

The two configurable options are the interval and the broadcast address.

Interval lets you adjust how often it will send a request.

Broadcast address is to handle setups where the network that Home Assistant sees, is not the actual local network, in here you can provide a new IP address to broadcast to. For example, if you are running this in a devcontainer, you will not see any results because broadcast packets are not forwarded by default, if you change this to your computers ip address, you should start to see replies.

This component only relays an event, it provides no functionallity for handling/managing discovered devices, that is left to separate components. This is so other compoments can take advantage of discovery without needing a hard coded reference or library.

[Developer info](./developer.md)
