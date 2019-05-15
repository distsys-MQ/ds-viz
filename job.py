from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, BinaryIO

if TYPE_CHECKING:
    from server import Server


class Job:
    def __init__(self, jid: int, cores: int):
        self.jid = jid
        self.cores = cores
        self.schd = None
        self.start = None
        self.end = None


def get_jobs(file: str, servers: Dict[str, Dict[int, Server]]) -> List[Job]:
    jobs = []

    with open(file, "rb") as f:
        while True:
            line = f.readline()

            if b"JOBN" in line:
                f.seek(-len(line), 1)
                jobs.append(make_job(f, servers))

            if not line:
                break

    get_job_times(file, job_list_to_dict(jobs))
    return jobs


def make_job(f: BinaryIO, servers: Dict[str, Dict[int, Server]]) -> Job:
    msg = f.readline().decode("utf-8").split()
    jid, cores = int(msg[3]), int(msg[5])

    while True:
        line = f.readline()

        if b"SCHD" in line:
            msg = line.decode("utf-8").split()
            server = servers[msg[3]][int(msg[4])]
            job = Job(int(msg[2]), cores)
            server.jobs.append(job)

            return job

        if not line:
            break


def job_list_to_dict(jobs: List[Job]) -> Dict[int, Job]:
    return {j.jid: j for j in jobs}


def get_job_times(file: str, jobs: Dict[int, Job]):
    with open(file, "r") as f:
        for line in f:
            if line.startswith("t:", 0, 2):
                msg = line.split()
                jid = int(msg[3])
                time = int(msg[1])

                # TODO try replacing with a dictionary
                #  https://docs.quantifiedcode.com/python-anti-patterns/readability/not_using_if_to_switch.html
                if "SCHEDULED" in msg:
                    jobs[jid].schd = time
                elif "RUNNING" in msg:
                    jobs[jid].start = time
                elif "COMPLETED" in msg:
                    jobs[jid].end = time
