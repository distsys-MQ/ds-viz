from typing import List, Dict
from xml.etree.ElementTree import parse


class Server:
    def __init__(self, kind: str, sid: int, cores: int):
        self.kind = kind
        self.sid = sid
        self.cores = cores
        self.jobs = []  # TODO add jobs


def get_servers() -> List[Server]:
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
