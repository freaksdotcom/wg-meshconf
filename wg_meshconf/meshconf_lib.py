from ipaddress import (
    IPv4Address,
    IPv6Address,
    IPv4Network,
    IPv6Network,
    ip_address,
    ip_network,
)
from typing import List, Text, Optional, Union
from dataclasses import dataclass, field
from wireguard import WireGuard
import functools

IPAddress = Union[IPv4Address, IPv6Address]
IPNetwork = Union[IPv4Network, IPv6Network]


DEFAULT_PORT = 51820


@dataclass
class Endpoint:
    address: Union[IPAddress, Text]
    port: int = DEFAULT_PORT

    def __post_init__(self) -> None:
        if isinstance(self.address, str):
            a, p = self.address.split(":")
            self.address = ip_address(a)
            self.port = int(p) if p else DEFAULT_PORT

    def __str__(self) -> Text:
        return ":".join([str(self.address), str(self.port)])


@dataclass
class WgPeer:
    name: Text
    address: List[IPNetwork]
    endpoint: Optional[Endpoint] = None
    allowed_ips: List[IPNetwork] = field(default_factory=list)
    listen_port: Optional[int] = None
    fw_mark: Optional[Text] = None
    private_key: Text = field(default_factory=WireGuard.genkey)
    dns: List[IPAddress] = field(default_factory=list)
    mtu: Optional[int] = None
    table: Optional[Text] = None
    preup: Optional[Text] = None
    postup: Optional[Text] = None
    predown: Optional[Text] = None
    postdown: Optional[Text] = None
    save_config: bool = False
    public_key: Optional[Text] = None

    _address: List[IPNetwork] = field(init=False, repr=False)
    _dns: List[IPAddress] = field(init=False, repr=False)
    _allowed_ips: List[IPNetwork] = field(init=False, repr=False)

    @property  # type: ignore
    def address(self) -> List[IPNetwork]:
        return self._address

    @address.setter
    def address(
        self, address: Union[List[Union[IPAddress, Text]], IPAddress, Text]
    ) -> None:
        if isinstance(address, list):
            self._address = [ip_network(a) for a in address]
        elif isinstance(address, str):
            self._address = [ip_network(a) for a in address.split(",")]
        else:
            self.address = [ip_network(address)]

    @property  # type:ignore
    def dns(self) -> List[IPAddress]:
        return self._dns

    @dns.setter
    def dns(self, dns_servers: Union[List[IPAddress], IPAddress, Text]) -> None:
        if dns_servers is None:
            dns_servers = []
        if isinstance(dns_servers, list):
            self._dns = [ip_address(a) for a in dns_servers]
        else:
            self.address = [ip_address(dns_servers)]

    def address_list(self) -> Text:
        return ", ".join([str(a) for a in self.address])

    def allowed_ips_list(self) -> Text:
        return ", ".join([str(a) for a in self.allowed_ips])

    def dns_list(self) -> Text:
        return ", ".join([str(a) for a in self.dns])

    @property  # type:ignore
    @functools.lru_cache(maxsize=None)
    def public_key(self) -> Text:
        return WireGuard.pubkey(self.private_key)

    @public_key.setter
    def public_key(self, *args, **kwargs) -> None:
        pass

    @property  # type:ignore
    def allowed_ips(self) -> List[IPNetwork]:
        return self._allowed_ips

    @allowed_ips.setter
    def allowed_ips(self, allowed_ips=List[IPNetwork]) -> None:
        self._allowed_ips = allowed_ips
