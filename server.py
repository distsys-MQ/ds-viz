from typing import Dict
from xml.etree.ElementTree import parse


class Server:
    def __init__(self, server):
        self.boot = int(server["bootupTime"])
        self.cores = int(server["coreCount"])
        self.memory = int(server["memory"])
        self.disk = int(server["disk"])


def get_servers() -> Dict[str, Dict[int, Server]]:
    res: Dict[str, Dict[int, Server]] = {}

    for serve in parse("system.xml").iter("server"):
        t = serve.attrib["type"]
        res[t] = {}

        for i in range(int(serve.attrib["limit"])):
            s = {a: serve.attrib[a] for a in serve.attrib if a not in ("type", "limit")}
            res[t][i] = Server(s)

    return res
