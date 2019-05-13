from typing import List
from xml.etree.ElementTree import parse


class Server:
    def __init__(self, kind: str, sid: int, cores: int):
        self.kind = kind
        self.sid = sid
        self.cores = cores


def get_servers() -> List[Server]:
    servers = []

    for s in parse("system.xml").iter("server"):
        for i in range(int(s.attrib["limit"])):
            servers.append(Server(s.attrib["type"], i, int(s.attrib["coreCount"])))

    return servers
