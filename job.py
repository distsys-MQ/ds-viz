from typing import Dict, List, BinaryIO


class Job:
    def __init__(self, jid: int, cores: int, memory, disk, schd: int = None,
                 start: int = None, end: int = None, failed: bool = False):
        self.jid = jid
        self.cores = cores
        self.memory = memory
        self.disk = disk
        self.schd = schd
        self.start = start
        self.end = end
        self.failed = failed

    def is_overlapping(self, job) -> bool:
        if self.start <= job.start and self.end >= job.end:  # self's runtime envelops job's runtime
            return True
        elif job.start <= self.start <= job.end:  # self starts during job's runtime
            return True
        elif job.start <= self.end <= job.end:  # self ends during job's runtime
            return True
        else:
            return False

    def is_running_at(self, t: int) -> bool:
        return self.start <= t <= self.end

    def copy(self):
        return Job(self.jid, self.cores, self.memory, self.disk, self.schd, self.start, self.end, self.failed)


def get_jobs(log: str, servers) -> List[Job]:
    jobs = []

    with open(log, "rb") as f:
        while True:
            line = f.readline()

            if b"JOB" in line:
                f.seek(-len(line), 1)
                jobs.append(make_job(f, servers))

            if not line:
                break

    return jobs


def make_job(f: BinaryIO, servers) -> Job:
    msg = f.readline().decode("utf-8").split()

    failed = True if msg[1] == "JOBF" else False
    schd = int(msg[2])
    jid = int(msg[3])
    cores = int(msg[5])
    memory = int(msg[6])
    disk = int(msg[7])

    while True:
        line = f.readline()

        if b"SCHD" in line:
            msg = line.decode("utf-8").split()
            job = Job(jid, cores, memory, disk, schd, failed=failed)
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

            if not line:
                break

            msg = line.split()

            if msg[1] == "JOBF" and int(msg[3]) == job.jid:
                job.failed = True
                job.end = time

                if job.start is None:
                    job.start = time

                break

            if line.startswith("t:", 0, 2):
                jid = int(msg[3])
                time = int(msg[1])

                if job.jid == jid:
                    if "RUNNING" in msg:
                        job.start = time
                    elif "COMPLETED" in msg:
                        job.end = time
                        break
