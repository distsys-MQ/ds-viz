from typing import Dict, List, BinaryIO


class Job:
    def __init__(self, jid: int, cores: int, memory, disk, schd: int = None, start: int = None,
                 end: int = None, failed: bool = False, fails: int = 0):
        self.jid = jid
        self.cores = cores
        self.memory = memory
        self.disk = disk
        self.schd = schd
        self.start = start
        self.end = end
        self.failed = failed
        self.fails = fails

    def is_overlapping(self, job: "Job") -> bool:
        if self.start <= job.start and self.end >= job.end:  # self's runtime envelops job's runtime
            return True
        elif job.start <= self.start <= job.end:  # self starts during job's runtime
            return True
        elif job.start <= self.end <= job.end:  # self ends during job's runtime
            return True
        else:
            return False

    def is_running_at(self, t: int) -> bool:
        return self.start <= t < self.end

    def is_queued_at(self, t: int) -> bool:
        return self.schd <= t < self.start

    def is_completed_at(self, t: int) -> bool:
        return not self.failed and self.end <= t

    def is_failed_at(self, t: int) -> bool:
        return self.failed and self.end <= t

    def copy(self) -> "Job":
        return Job(self.jid, self.cores, self.memory, self.disk, self.schd,
                   self.start, self.end, self.failed, self.fails)

    def set_job_times(self, log: str, pos: int, job_failures: Dict[int, int]) -> None:
        with open(log, "rb") as f:
            f.seek(pos, 0)

            while True:
                line = f.readline().decode("utf-8")

                if not line:
                    break

                msg = line.split()

                if msg[1] == "JOBF" and int(msg[3]) == self.jid:
                    self.failed = True
                    job_failures[self.jid] += 1
                    self.fails = job_failures[self.jid]
                    self.end = time

                    if self.start is None:
                        self.start = time

                    break

                if line.startswith("t:", 0, 2):
                    jid = int(msg[3])
                    time = int(msg[1])

                    if self.jid == jid:
                        if "RUNNING" in msg:
                            self.start = time
                        elif "COMPLETED" in msg:
                            self.end = time
                            break


# noinspection PyUnresolvedReferences
def get_jobs(log: str, servers: Dict[str, Dict[int, "Server"]]) -> None:
    job_failures = dict()

    with open(log, "rb") as f:
        while True:
            line = f.readline()

            if b"JOB" in line:
                f.seek(-len(line), 1)
                make_job(f, servers, job_failures)

            if not line:
                break


# noinspection PyUnresolvedReferences
def make_job(f: BinaryIO, servers: Dict[str, Dict[int, "Server"]], job_failures: Dict[int, int]) -> Job:
    msg = f.readline().decode("utf-8").split()

    schd = int(msg[2])
    jid = int(msg[3])
    cores = int(msg[5])
    memory = int(msg[6])
    disk = int(msg[7])
    fails = 0

    if jid not in job_failures:
        job_failures[jid] = 0

    if msg[1] == "JOBF":
        fails = job_failures[jid]

    while True:
        line = f.readline()

        if b"SCHD" in line:
            msg = line.decode("utf-8").split()
            job = Job(jid, cores, memory, disk, schd, fails=fails)
            job.set_job_times(f.name, f.tell(), job_failures)

            server = servers[msg[3]][int(msg[4])]
            server.jobs.append(job)

            return job

        if not line:
            break


def job_list_to_dict(jobs: List[Job]) -> Dict[int, Job]:
    return {j.jid: j for j in jobs}
