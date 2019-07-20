from typing import List, Dict, BinaryIO
from xml.etree.ElementTree import parse

from job import get_jobs
from server_failure import ServerFailure, get_failures


class Server:
    def __init__(self, kind: str, sid: int, cores: int):
        self.kind = kind
        self.sid = sid
        self.cores = cores
        self.jobs = []
        self.failures: List[ServerFailure] = []


def get_servers(file: str) -> List[Server]:
    with open(file, "rb") as f:
        while True:
            line = f.readline()

            if b"RESC All" in line:
                servers = make_servers(f)
                s_dict = server_list_to_dict(servers)
                get_jobs(file, s_dict)
                get_failures(file, s_dict)

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


def get_servers_from_system(file: str, system: str) -> List[Server]:
    servers = []

    for s in parse(system).iter("server"):
        for i in range(int(s.attrib["limit"])):
            servers.append(Server(s.attrib["type"], i, int(s.attrib["coreCount"])))

    s_dict = server_list_to_dict(servers)
    get_jobs(file, s_dict)
    get_failures(file, s_dict)

    return servers


def server_list_to_dict(servers: List[Server]) -> Dict[str, Dict[int, Server]]:
    s_dict = {}

    for s in servers:
        if s.kind not in s_dict:
            s_dict[s.kind] = {}

        s_dict[s.kind][s.sid] = s

    return s_dict


def get_results(file: str) -> str:
    with open(file, 'r') as f:
        for line in f:  # Could be more efficient if read from the end of file
            if "RCVD QUIT" in line:
                for l in f:
                    if l[0] == '#':
                        return ''.join(f.readlines())
