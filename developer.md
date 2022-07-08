Developer information

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
