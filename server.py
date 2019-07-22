from typing import List, Dict, BinaryIO
from xml.etree.ElementTree import parse

from file_read_backwards import FileReadBackwards

from job import get_jobs
from server_failure import ServerFailure, get_failures


class Server:
    last_time = None

    def __init__(self, kind: str, sid: int, cores: int):
        self.kind = kind
        self.sid = sid
        self.cores = cores
        self.jobs = []
        self.failures: List[ServerFailure] = []


def get_servers(log: str) -> List[Server]:
    with open(log, "rb") as f:
        while True:
            line = f.readline()

            if b"RESC All" in line:
                servers = make_servers(f)
                s_dict = server_list_to_dict(servers)
                get_jobs(log, s_dict)
                get_failures(log, s_dict, Server.last_time)

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


def get_servers_from_system(log: str, system: str) -> List[Server]:
    last_time = get_last_time(log, system)
    servers = []

    for s in parse(system).iter("server"):
        for i in range(int(s.attrib["limit"])):
            servers.append(Server(s.attrib["type"], i, int(s.attrib["coreCount"])))

    s_dict = server_list_to_dict(servers)
    get_jobs(log, s_dict)
    get_failures(log, s_dict, last_time)

    return servers


def server_list_to_dict(servers: List[Server]) -> Dict[str, Dict[int, Server]]:
    s_dict = {}

    for s in servers:
        if s.kind not in s_dict:
            s_dict[s.kind] = {}

        s_dict[s.kind][s.sid] = s

    return s_dict


def get_results(log: str) -> str:
    with FileReadBackwards(log, encoding="utf-8") as f:
        results = []

        while True:
            line = f.readline().replace("\r\n", "\n")
            results.append(line)

            if "SENT QUIT" in line:
                return ''.join(reversed(results[:-2]))


def get_end_time(system: str) -> int:
    root = parse(system).getroot()
    term = next(filter(lambda node: "endtime" == node.get("type"), root.find("termination").findall("condition")))
    return int(term.get("value"))


def get_last_job_time(log: str) -> int:
    with FileReadBackwards(log, encoding="utf-8") as f:
        while True:
            line = f.readline()

            if line.startswith("t:", 0, 2):
                return int(line.split()[1])


def get_last_time(log: str, system: str) -> int:
    end_time = get_end_time(system)
    last_job_time = get_last_job_time(log)

    last_time = max(end_time, last_job_time)
    Server.last_time = last_time
    return last_time
