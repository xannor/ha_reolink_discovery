Developer information

Update #2:

The discovery signal approach is still valid, but I also added config_flow push discovery as well.

If you add the following to your integration, you can intercept and handle new device discoverys on the users network.

```
    async def async_step_discovery(self, discovery_info: DiscoveryInfoType):
        return await super().async_step_discovery(discovery_info)

```

the discovery_info will be a dict that follows the structure of DiscoveredDeviceType below, self.initial_data will also be set to the same dict

----

<del>
The current output of the component is a follows

```
{
    "event_type": "reolink_discovery",
    "data": {
        "ip": "x.x.x.x",
        "mac": "xx:xx:xx:xx:xx:xx",
        "name": "Camera1",
        "ident": "",
        "uuid": "..."
    },
}
```
</del>

Update: the component has been re-worked to use the discovery helper and dispatching instead of events, this should be lower overhead as no dict->json->dict conversion will be happening. the data poriton is the same and the service is "reolink_discovery"
use
```
homeassistant.helpers.discovery.async_listener("reolink_discovery", __callback)
```
here callback is
```
async def __callback(service:str, info:DiscoveryIntoType)->None:
```
set this up in async_setup to make sure it is loaded as soon as the component is.

I also added an option for a notifier, the name entered into this option is the component that will be notified on each event.
This means that in the discovery system will attemp to load that component before dispatch.
/:Update

the python typedef for the above data block is:

```
class DiscoveredDeviceType(TypedDict):
    """Discovered Device"""

    ip: str
    mac: str
    name: NotRequired[str]
    ident: NotRequired[str]
    uuid: NotRequired[str]
```

Notes:

IP and mac are guarenteed because of the UDP message, most devices I have tested with provide name and uuid, though it is possible some could not (they have a lot of different devices).

The ident field is just a guess, I only have one device that provides data in that field, and it is not a web enabled device.
So far seeing IPC in that field mean a web based component can ingore the device.

There is some other data in the packet, but I cannot determine what it could mean with the range of devices I currently posses. Running this component in debug mode will log more information about the packets.

If you done want the trace info in debug you can add a filter the logger to remove "^Packet Trace:"
