#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: wg-meshconf
Creator: K4YT3X
Date Created: July 19, 2020
Last Modified: January 12, 2021

Licensed under the GNU General Public License Version 3 (GNU GPL v3),
    available at: https://www.gnu.org/licenses/gpl-3.0.txt
(C) 2018-2021 K4YT3X
"""

# built-in imports
import argparse
import pathlib
import sys
from ipaddress import ip_address, ip_network

# local imports
from database_manager import DatabaseManager
from meshconf_lib import WgPeer, Endpoint


def parse_arguments() -> argparse.Namespace:
    """parse CLI arguments"""
    parser = argparse.ArgumentParser(
        prog="wg-meshconf", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-d",
        "--database",
        type=argparse.FileType("r+"),
        help="path where the database file is stored",
        default=pathlib.Path("database.json"),
    )

    # add subparsers for commands
    subparsers = parser.add_subparsers(dest="command")

    peer_args = argparse.ArgumentParser(add_help=False)
    peer_args.add_argument(
        "name",
        type=str,
        help="Name used to identify this node",
    )
    peer_args.add_argument(
        "--address",
        type=ip_network,
        help="address of the server",
        action="append",
        required=True,
    )
    peer_args.add_argument(
        "--endpoint",
        type=Endpoint,
        help="peer's public endpoint address",
    )
    peer_args.add_argument(
        "--allowedips",
        type=ip_network,
        help="additional allowed IP addresses",
        action="append",
    )
    peer_args.add_argument(
        "--privatekey",
        type=str,
        help="private key of server interface",
    )
    peer_args.add_argument(
        "--listenport", type=int, help="port to listen on", default=51820
    )
    peer_args.add_argument(
        "--fwmark",
        type=str,
        help="fwmark for outgoing packets",
    )
    peer_args.add_argument(
        "--dns",
        type=ip_address,
        help="server interface DNS servers",
        action="append",
    )
    peer_args.add_argument(
        "--mtu",
        type=int,
        help="server interface MTU",
    )
    peer_args.add_argument(
        "--table",
        type=str,
        help="server routing table",
    )
    peer_args.add_argument(
        "--table_file",
        type=pathlib.Path,
        help="server routing table",
    )
    peer_args.add_argument(
        "--preup",
        type=str,
        help="command to run before interface is up",
    )
    peer_args.add_argument(
        "--postup",
        type=str,
        help="command to run after interface is up",
    )
    peer_args.add_argument(
        "--predown",
        type=str,
        help="command to run before interface is down",
    )
    peer_args.add_argument(
        "--postdown",
        type=str,
        help="command to run after interface is down",
    )
    peer_args.add_argument(
        "--saveconfig",
        action="store_true",
        help="save server interface to config upon shutdown",
        default=False,
    )

    # add new peer
    subparsers.add_parser("addpeer", parents=[peer_args])

    # update existing peer information
    subparsers.add_parser("updatepeer", parents=[peer_args])

    # delpeer deletes a peer form the database
    delpeer = subparsers.add_parser("delpeer")
    delpeer.add_argument("name", help="Name of peer to delete")

    # showpeers prints a table of all peers and their configurations
    showpeers = subparsers.add_parser("showpeers")
    showpeers.add_argument(
        "name",
        help="Name of the peer to query",
        nargs="?",
    )
    showpeers.add_argument(
        "--style",
        choices=["table", "text"],
        help="peers information printing style",
        default="table",
    )
    showpeers.add_argument(
        "-s",
        "--simplify",
        help="do not print columns that are all None",
        action="store_true",
    )

    # generate config
    genconfig = subparsers.add_parser("genconfig")
    genconfig.add_argument(
        "name",
        help="Name of the peer to generate configuration for, \
            configuration for all peers are generated if omitted",
        nargs="?",
    )
    genconfig.add_argument(
        "-o",
        "--output",
        help="configuration file output directory",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parent.absolute() / "output",
    )

    return parser.parse_args()


# if the file is not being imported
def main() -> None:

    args = parse_arguments()

    database_manager = DatabaseManager(args.database)

    if args.command == "addpeer":
        database_manager.addpeer(
            WgPeer(
                args.name,
                args.address,
                args.endpoint,
                args.allowedips,
                args.listenport,
                args.fwmark,
                args.privatekey,
                args.dns,
                args.mtu,
                args.table,
                args.preup,
                args.postup,
                args.predown,
                args.postdown,
                args.saveconfig,
            )
        )

    elif args.command == "updatepeer":
        database_manager.updatepeer(
            WgPeer(
                args.name,
                args.address,
                args.endpoint,
                args.allowedips,
                args.listenport,
                args.fwmark,
                args.privatekey,
                args.dns,
                args.mtu,
                args.table,
                args.preup,
                args.postup,
                args.predown,
                args.postdown,
                args.saveconfig,
            )
        )

    elif args.command == "delpeer":
        database_manager.delpeer(args.name)

    elif args.command == "showpeers":
        database_manager.showpeers(args.name, args.style, args.simplify)

    elif args.command == "genconfig":
        database_manager.genconfig(args.name, args.output)

    # if no commands are specified
    else:
        print(
            "No command specified\nUse wg-meshconf --help to see available commands",
            file=sys.stderr,
        )


# launch the main function if it is not imported as a package
if __name__ == "__main__":
    main()
