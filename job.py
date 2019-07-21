from typing import Dict, List, BinaryIO


class Job:
    def __init__(self, jid: int, cores: int, schd: int = None, start: int = None, end: int = None):
        self.jid = jid
        self.cores = cores
        self.schd = schd
        self.start = start
        self.end = end


def get_jobs(log: str, servers) -> List[Job]:
    jobs = []

    with open(log, "rb") as f:
        while True:
            line = f.readline()

            if b"JOBN" in line:
                f.seek(-len(line), 1)
                jobs.append(make_job(f, servers))

            if not line:
                break

    return jobs


def make_job(f: BinaryIO, servers) -> Job:
    msg = f.readline().decode("utf-8").split()
    cores = int(msg[5])

    while True:
        line = f.readline()

        if b"SCHD" in line:
            msg = line.decode("utf-8").split()
            job = Job(int(msg[2]), cores)
            get_job_times(f.name, f.tell(), job)

            server = servers[msg[3]][int(msg[4])]
            server.jobs.append(job)

            return job

        if not line:
            break


def job_list_to_dict(jobs: List[Job]) -> Dict[int, Job]:
    return {j.jid: j for j in jobs}


def get_job_times(log: str, pos: int, job: Job):
    with open(log, "rb") as f:
        f.seek(pos, 0)

        while True:
            line = f.readline().decode("utf-8")

            if line.startswith("t:", 0, 2):
                msg = line.split()
                jid = int(msg[3])
                time = int(msg[1])

                if job.jid == jid:
                    if "SCHEDULED" in msg:
                        job.schd = time
                    elif "RUNNING" in msg:
                        job.start = time
                    elif "COMPLETED" in msg:
                        job.end = time
                        break

            if not line:
                break
