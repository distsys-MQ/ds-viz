from typing import List, BinaryIO

file = "ds-config2-ff.txt"


class Job:
    def __init__(self, jid: int, cores: int):
        self.jid = jid
        self.cores = cores
        self.schd = None
        self.start = None
        self.end = None


def get_jobs(servers) -> List[Job]:
    jobs = []

    with open(file, "rb") as f:
        while True:
            line = f.readline()

            if b"JOBN" in line:
                f.seek(-len(line), 1)
                job = make_job(f, servers)
                jobs.append(job)

            if not line:
                break

    return jobs


def make_job(f: BinaryIO, servers) -> Job:
    msg = f.readline().decode("utf-8").split(" ")
    jid, cores = int(msg[3]), int(msg[5])

    while True:
        line = f.readline()

        if b"SCHD" in line:
            msg = line.decode("utf-8").strip().split(" ")
            server = servers[msg[3]][int(msg[4])]
            job = Job(int(msg[2]), cores)
            server.jobs.append(job)

            return job

        if not line:
            break
