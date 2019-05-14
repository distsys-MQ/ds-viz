from typing import List, BinaryIO

from server import Server, get_servers, server_list_to_dict

file = "ds-config2-ff.txt"
servers = server_list_to_dict(get_servers())


class Job:
    def __init__(self, jid: int, cores: int, server: Server):
        self.jid = jid
        self.cores = cores
        self.server = server
        self.schd = None
        self.start = None
        self.end = None


def get_jobs() -> List[Job]:
    jobs = []

    with open(file, "rb") as f:
        while True:
            line = f.readline()

            if b"JOBN" in line:
                f.seek(-len(line), 1)
                job = make_job(f)
                jobs.append(job)

            if not line:
                break

    return jobs


def make_job(f: BinaryIO) -> Job:
    msg = f.readline().decode("utf-8").split(" ")
    jid, cores = int(msg[3]), int(msg[5])

    while True:
        line = f.readline()

        if b"SCHD" in line:
            msg = line.decode("utf-8").split(" ")
            server = servers[msg[3]][int(msg[4])]
            job = Job(int(msg[2]), cores, server)

            return job

        if not line:
            break
