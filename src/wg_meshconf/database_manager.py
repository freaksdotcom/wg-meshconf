# -*- coding: utf-8 -*-
# pyre-strict
"""
Name: Database Manager
Creator: K4YT3X
Date Created: July 19, 2020
Last Modified: January 12, 2021
"""

# built-in imports
import sys

if sys.platform == "win32":
    import msvcrt
else:
    import fcntl
import json
import pathlib
import pprint
from contextlib import contextmanager, suppress
from dataclasses import asdict, fields, replace
from typing import Any, Dict, Generator, List, Set, Text, Union

# third party imports
import pystache

with suppress(ImportError):
    from prettytable import PrettyTable

# local imports
from config_template import CONFIG_TEMPLATE
from meshconf_lib import WgPeer


@contextmanager
def peer_database(
    file: pathlib.Path, update: bool = False, *args: Any, **kwargs: Any
) -> Generator[Dict[Text, WgPeer], None, None]:
    """Context manager for the JSON data file."""
    peers: Dict[Text, WgPeer] = {}
    print(file)
    if not file.exists():
        f_mode = "w+"
    else:
        f_mode = "r+"
    with open(file, mode=f_mode, encoding="utf-8") as database_file:
        database_file.seek(0, 0)
        try:
            if sys.platform == "win32":

                msvcrt.locking(database_file.fileno(), msvcrt.LK_LOCK, 1)
            else:
                fcntl.flock(database_file, fcntl.LOCK_EX)
            try:
                peer_db = json.load(database_file)
                peers = {
                    k: replace(WgPeer(""), **v) for k, v in peer_db["peers"].items()
                }
                del peer_db
            except:  # noqa
                pass
            yield peers
        finally:
            if update:
                peer_db = {"peers": {p.name: p for p in peers.values() if p.name}}
                pprint.pprint({p.name: p for p in peers.values() if p.name})

                database_file.seek(0, 0)
                json.dump(peer_db, database_file, indent=4)
                database_file.flush()

                if sys.platform == "win32":
                    database_file.seek(0)
                    msvcrt.locking(database_file.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(database_file, fcntl.LOCK_UN)


class DatabaseManager:
    def __init__(self, database_path: pathlib.Path) -> None:
        self.database_path = database_path

    def addpeer(self, peer: WgPeer) -> None:
        with peer_database(self.database_path, update=True) as peer_db:
            if peer.name in peer_db:
                raise KeyError(f"Peer with name {peer.name} already exists")
            peer_db[peer.name] = peer

    def updatepeer(self, peer: WgPeer) -> None:
        with peer_database(self.database_path, update=True) as peer_db:
            if peer.name not in peer_db:
                raise KeyError(f"Peer with name {peer.name} does not exist")
            peer_db[peer.name] = peer

    def delpeer(self, name: str) -> None:
        with peer_database(self.database_path, update=True) as peer_db:
            try:
                del peer_db[name]
            except KeyError:
                raise KeyError(f"Peer with ID {name} does not exist")

    def showpeers(
        self,
        name: Union[Text, Set[Text], List[Text]],
        style: str = "table",
        simplify: bool = False,
    ) -> None:
        with peer_database(self.database_path) as peer_db:
            if isinstance(name, str):
                name = {name}
            elif name is None:
                name = set()
            else:
                name = set(name)

            field_names = {"name": None}

            # exclude all columns that only have None's in simplified mode
            if simplify:
                field_names.update(
                    {
                        f.name: None
                        for p in peer_db.values()
                        for f in fields(p)
                        if getattr(p, f.name) and f.name not in field_names
                    }
                )
            # include all columns by default
            else:
                field_names.update(
                    {f.name: None for f in fields(WgPeer) if f.name not in field_names}
                )

            # if the style is table
            # print with prettytable
            if style == "table":
                table = PrettyTable()
                table.field_names = field_names.keys()

                for peer in peer_db.values():
                    table.add_row(
                        [peer.name]
                        + [
                            getattr(peer, k)
                            if not isinstance(getattr(peer, k), list)
                            else ",".join(getattr(peer, k))
                            for k in [i for i in table.field_names if i != "name"]
                        ]
                    )

                print(table)

            # if the style is text
            # print in plaintext format
            elif style == "text":
                for peer in peer_db.values():
                    print(f"{'peer': <14}{peer.name}")
                    for key in field_names:
                        print(f"{key: <14}{getattr(peer, key)}") if not isinstance(
                            getattr(peer, key), list
                        ) else print(f"{key: <14}{','.join(getattr(peer, key))}")
                    print()

    def genconfig(
        self, name: Union[Text, List[Text], Set[Text]], output: pathlib.Path
    ) -> None:
        with peer_database(self.database_path) as peer_db:
            # check if output directory is valid
            # create output directory if it does not exist
            if output.exists() and not output.is_dir():
                raise FileExistsError(
                    "Error: output path already exists and is not a directory"
                )
            elif not output.exists():
                print(f"Creating output directory: {output}")
                output.mkdir(exist_ok=True)

            template = pystache.parse(CONFIG_TEMPLATE)
            renderer = pystache.Renderer()
            for peer in peer_db.values():
                with (output / f"{peer.name}.conf").open("w") as config:
                    config.write(
                        renderer.render(
                            template,
                            {
                                "host": peer,
                                "peers": [
                                    {"peer": asdict(p)} for p in peer_db.values()
                                ],
                            },
                        )
                    )
