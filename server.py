import sys
from itertools import chain
from textwrap import dedent
from typing import List, Dict, BinaryIO
from xml.etree.ElementTree import parse

from file_read_backwards import FileReadBackwards

from job import Job, get_jobs
from server_failure import ServerFailure, get_failures
from server_state import ServerState as state


class Server:
    last_time: int = None

    def __init__(self, kind: str, sid: int, cores: int, memory: int, disk: int,
                 states: Dict[int, state] = None, jobs: List[Job] = None,
                 failures: List[ServerFailure] = None):
        self.kind = kind
        self.sid = sid
        self.cores = cores
        self.memory = memory
        self.disk = disk
        self.states = states if states else {0: state.inactive}
        self.jobs = jobs if jobs else []
        self.failures = failures if failures else []

    def __str__(self):
        return f"{self.kind} {self.sid}"

    def get_server_at(self, t: int) -> "Server":
        jobs = list(filter(lambda j: j.is_running_at(t), self.jobs))
        cores = self.cores - sum(j.cores for j in jobs)
        memory = self.memory - sum(j.memory for j in jobs)
        disk = self.disk - sum(j.disk for j in jobs)
        states = {0: self.get_state_at(t)}

        return Server(self.kind, self.sid, cores, memory, disk, states, jobs)

    def get_state_at(self, t: int) -> state:
        best = None
        diff = sys.maxsize

        for time, stat in self.states.items():
            d = t - time

            if d == 0:
                return stat
            elif 0 < d < diff:
                best = stat
                diff = d
        return best

    def count_failures_at(self, t: int) -> int:
        res = 0

        for time in sorted(self.states):
            if time > t:
                break
            if self.states[time] == state.unavailable:
                res += 1
        return res

    def print_server_at(self, t: int) -> str:
        # TODO Add more details
        cur = self.get_server_at(t)

        queued_jobs = list(filter(lambda j: j.is_queued_at(t), self.jobs))
        completed_jobs = list(filter(lambda j: j.is_completed_at(t), self.jobs))
        failed_jobs = list(filter(lambda j: j.is_failed_at(t), self.jobs))

        return (
            f"{self.kind} {self.sid}: {cur.states[0].name},  "
            f"cores: {cur.cores} ({self.cores}),  "
            f"memory: {cur.memory} ({self.memory}),\n"
            f"disk: {cur.disk} ({self.disk}),  "
            f"running jobs: {len(cur.jobs)},  "
            f"queued jobs: {len(queued_jobs)},\n"
            f"completed jobs: {len(completed_jobs)},  "
            f"failed jobs: {len(failed_jobs)},  "
            f"server failures: {self.count_failures_at(t)}"
        )

    def get_server_states(self, log: str) -> None:
        states = {0: state.inactive}

        with open(log, "r") as f:
            while True:
                line = f.readline()

                if not line:
                    break

                msg = line.split()

                if msg[0] == "t:":
                    lat = msg[msg.index('#') + 1:]
                    time = int(msg[1])
                    sid = int(lat[0])
                    kind = lat[3]

                    if kind == self.kind and sid == self.sid:
                        if "(booting)" in msg:
                            states[time] = state.booting
                        elif "RUNNING" in msg and states[max(states)] is not state.active:
                            states[time] = state.active
                        elif "COMPLETED" in msg and time != Server.last_time and len(
                                list(filter(lambda j: j.is_running_at(time + 1), self.jobs))) == 0:
                            states[time + 1] = state.idle

        for f in self.failures:
            states[f.fail] = state.unavailable

            if f.recover != Server.last_time:
                states[f.recover] = state.inactive

        self.states = states


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


def get_servers_from_system(log: str, system: str) -> List[Server]:
    Server.last_time = get_last_time(log, system)
    servers = []

    for s in parse(system).iter("server"):
        for i in range(int(s.attrib["limit"])):
            servers.append(Server(
                s.attrib["type"], i, int(s.attrib["coreCount"]), int(s.attrib["memory"]), int(s.attrib["disk"])))

    s_dict = server_list_to_dict(servers)
    get_jobs(log, s_dict)
    get_failures(log, s_dict, Server.last_time)

    for s in servers:
        s.get_server_states(log)

    return servers


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
            servers.append(Server(msg[1], int(msg[2]), int(msg[5]), int(msg[6]), int(msg[7])))

    return servers


def get_results(log: str) -> str:
    with FileReadBackwards(log, encoding="utf-8") as f:
        results = []

        while True:
            line = f.readline().replace("\r\n", "\n")
            results.append(line[2:])  # Remove '#'s

            if "SENT QUIT" in line:
                results.pop(2)  # Remove "[ Overall ]" line
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
    return last_time


def print_servers_at(servers: List[Server], t: int) -> str:
    curs = [s.get_server_at(t) for s in servers]

    s_inactive = list(filter(lambda s: s.states[0] == state.inactive, curs))
    s_booting = list(filter(lambda s: s.states[0] == state.booting, curs))
    s_idle = list(filter(lambda s: s.states[0] == state.idle, curs))
    s_active = list(filter(lambda s: s.states[0] == state.active, curs))
    s_unavailable = list(filter(lambda s: s.states[0] == state.unavailable, curs))
    s_failures = sum(s.count_failures_at(t) for s in servers)

    j_running = [j for s in curs for j in s.jobs]
    j_queued = list(chain.from_iterable(filter(lambda job: job.is_queued_at(t), s.jobs) for s in servers))
    j_completed = list(chain.from_iterable(filter(lambda job: job.is_completed_at(t), s.jobs) for s in servers))
    j_failed = list(chain.from_iterable(filter(lambda job: job.is_failed_at(t), s.jobs) for s in servers))

    return (
        f"SERVERS: inactive: {len(s_inactive)},  "
        f"booting: {len(s_booting)},  "
        f"idle: {len(s_idle)},  "
        f"active: {len(s_active)},\n"
        f"  unavailable: {len(s_unavailable)} ({s_failures})\n"
        f"JOBS: running: {len(j_running)},  "
        f"queued: {len(j_queued)},  "
        f"completed: {len(j_completed)},  "
        f"failed: {len(j_failed)}"
    )


def server_list_to_dict(servers: List[Server]) -> Dict[str, Dict[int, Server]]:
    s_dict = {}

    for s in servers:
        if s.kind not in s_dict:
            s_dict[s.kind] = {}

        s_dict[s.kind][s.sid] = s

    return s_dict
