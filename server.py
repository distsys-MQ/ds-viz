from typing import List, Dict, BinaryIO
from xml.etree.ElementTree import parse

from job import get_jobs


class Server:
    def __init__(self, kind: str, sid: int, cores: int):
        self.kind = kind
        self.sid = sid
        self.cores = cores
        self.jobs = []


def get_servers(file: str) -> List[Server]:
    with open(file, "rb") as f:
        while True:
            line = f.readline()

            if b"RESC All" in line:
                servers = make_servers(f)
                get_jobs(file, server_list_to_dict(servers))

                return servers

            if not line:
                break


def make_servers(f: BinaryIO) -> List[Server]:
    servers = []

    while True:
        line = f.readline()

        if not line:
            break

        msg = line.decode("utf-8").split()

        if "." in msg:
            break

        if not any([i in msg for i in ["OK", "DATA"]]):
            servers.append(Server(msg[1], int(msg[2]), int(msg[5])))

    return servers


def get_servers_from_system() -> List[Server]:
    servers = []

    for s in parse("system.xml").iter("server"):
        for i in range(int(s.attrib["limit"])):
            servers.append(Server(s.attrib["type"], i, int(s.attrib["coreCount"])))

    return servers


def server_list_to_dict(servers: List[Server]) -> Dict[str, Dict[int, Server]]:
    s_dict: Dict[str, Dict[int, Server]] = {}

    for s in servers:
        if s.kind not in s_dict:
            s_dict[s.kind] = {}

        s_dict[s.kind][s.sid] = s

    return s_dict
