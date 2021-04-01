import textwrap
from typing import Text

__ALL__ = ["CONFIG_TEMPLATE"]

CONFIG_TEMPLATE: Text = textwrap.dedent(
    """\
    [Interface]
    # Name: {{host.name}}
    Address = {{host.address_list}}
    PrivateKey = {{host.private_key}}
    {{#host.listen_port}}
    ListenPort = {{host.listen_port}}
    {{/host.listen_port}}
    {{#host.fw_mark}}
    FwMark = {{host.fw_mark}}
    {{/host.fw_mark}}
    {{#host.dns}}
    DNS = {{host.dns_list}}
    {{/host.dns}}
    {{#host.mtu}}
    MTU = {{host.mtu}}
    {{/host.mtu}}
    {{#host.table}}
    Table = {{host.table}}
    {{/host.table}}
    {{#host.preup}}
    PreUp = {{host.preup}}
    {{/host.preup}}
    {{#host.postup}}
    PostUp = {{host.postup}}
    {{/host.postup}}
    {{#host.predown}}
    PreDown = {{host.predown}}
    {{/host.predown}}
    {{#host.postdown}}
    PostDown = {{host.postdown}}
    {{/host.postdown}}
    {{#host.save_config}}
    SaveConfig = {{host.save_config}}
    {{/host.save_config}}
    {{#peers}}

    [Peer]
    # Name: {{peer.name}}
    PublicKey = {{peer.public_key}}
    {{#endpoint}}
    Endpoint = {{peer.endpoint}}:{{peer.listen_port}}
    {{/endpoint}}
    {{#allowed_ips}}
    AllowedIPs = {{peer.allowed_ips_list}}
    {{/allowed_ips}}
    {{/peers}}
    """
)
