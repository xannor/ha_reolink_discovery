"""Core implementation"""

from __future__ import annotations

from asyncio import DatagramProtocol, DatagramTransport, get_event_loop
import logging
import socket
from struct import pack
from typing import Callable, Final

from .typing import ReolinkDiscoveryInfo

PORT: Final = 3000
PING: Final = 2000

# the cameras expect this value and reply with it as a checksum
PING_MESSAGE: Final = pack("!L", 0xAAAA0000)


def _nulltermstring(value: bytes, offset: int, maxlength: int = None) -> str | None:
    idx = value.index(0, offset)
    if idx <= offset:
        return None
    if maxlength is not None and offset - idx > maxlength:
        idx = offset + maxlength
    return value[offset:idx].decode("ascii")


DISCOVERY_CALLBACK = Callable[[ReolinkDiscoveryInfo],None]

class ReolinkDiscoveryProtocol(DatagramProtocol):
    """UDP Discovery Protocol"""

    def __init__(
        self, *, callback:DISCOVERY_CALLBACK = None, logger: logging.Logger = None, ping_message: bytes = PING_MESSAGE
    ) -> None:
        self._logger = logger
        self._transport: DatagramTransport = None
        self._reply_verify = ping_message
        self._callback = callback

    def connection_made(self, transport: DatagramTransport) -> None:
        self._transport = transport
        if self._logger:
            self._logger.debug(
                "Listener connected %s", transport.get_extra_info("sockname")
            )

    def connection_lost(self, exc: Exception | None) -> None:
        if exc is not None and self._logger:
            self._logger.error("Listener received error")
        self._transport = None
        if self._logger:
            self._logger.debug("Listener disconnected")

    def datagram_received(self, data: bytes, addr: tuple[str | any, int]) -> None:
        if len(data) != 388:
            return

        # pylint: disable=line-too-long
        # offsets
        # 50+8   - flags?
        # 58+18  - zero padded identifier string? Lumus (only?) sends "IPC" here
        # 80+6   - binary MAC
        # 104+4  - replay of ping message? need to confirm if it is a repeat or always the "original"
        # 108+16 - zero padded ip string +4, not sure if they went 20chars or if there is a 4 byte data point
        # 128+4  - another marker? consistently 0x28230000
        # 132+32 - zero padded name string
        # 164+18 - zero padded MAC string
        # 228+16 - zero padded UUID string, not sure how long this could be as there is a lot of padding

        if data[104:108] != self._reply_verify:
            return

        self._logger.debug(
            "Packet Trace: %r; %r; %r; %r; %r; %r; %r",
            data[50:58],
            data[128:132],
            data[0:50].strip(b"\0").rstrip(b"\0"),
            data[62:80].strip(b"\0").rstrip(b"\0"),
            data[86:104].strip(b"\0").rstrip(b"\0"),
            data[148:164].strip(b"\0").rstrip(b"\0"),
            data[244:].strip(b"\0").rstrip(b"\0"),
        )

        self._discovery_callback(ReolinkDiscoveryInfo(
            ip=_nulltermstring(data, 108, 20),
            macaddress=_nulltermstring(data, 164, 18) or data[80:86].hex(":"),
            hostname=_nulltermstring(data, 132, 32) or "",
            ident=_nulltermstring(data, 58, 18),
            uuid=_nulltermstring(data, 228, 32),
        ))

    def _discovery_callback(self, device: ReolinkDiscoveryInfo) -> None:
        if self._logger:
            self._logger.debug("Discovered %s", device)
        if self._callback:
            self._callback(device)

    @classmethod
    async def async_create_listener(cls, discovered:DISCOVERY_CALLBACK=None, address:str = "0.0.0.0", port:int = PORT, logger:logging.Logger=None, **kwargs):
        """Create Discovery listener"""

        if logger:
            logger.debug("Listening on %s", address)

        def _factory():
            return cls(logger=logger, callback=discovered, **kwargs)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((address, port))
        return await get_event_loop().create_datagram_endpoint(_factory, sock=sock)

    @staticmethod
    def async_ping(address: str = "255.255.255.255", port: int = PING):
        """Send discovery ping to network"""

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        return sock.sendto(PING_MESSAGE, (address, port))

