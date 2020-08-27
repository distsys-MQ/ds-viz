import sys
from collections import OrderedDict
from typing import Dict, List


class Job:
    # noinspection PyUnresolvedReferences
    def __init__(self, jid: int, cores: int, memory, disk, schd: int = None, start: int = None,
                 end: int = None, will_fail: bool = False, fails: int = 0, server: "Server" = None):
        self.jid = jid
        self.cores = cores
        self.memory = memory
        self.disk = disk
        self.schd = schd
        self.start = start
        self.end = end
        self.will_fail = will_fail
        self.fails = fails
        self.server = server
        self.last_core = None

    def __str__(self) -> str:
        return "j{} {}:{}:{} f{}".format(self.jid, self.schd, self.start, self.end, self.fails)

    def is_overlapping(self, job: "Job") -> bool:
        if self.jid == job.jid:  # Job can't overlap itself
            return False
        if self.start <= job.start and self.end >= job.end:  # self's runtime envelops job's runtime
            return True
        elif job.start < self.start <= job.end:  # self starts during job's runtime
            return True
        elif job.start < self.end <= job.end:  # self ends during job's runtime
            return True
        else:
            return False

    def is_running_at(self, t: int) -> bool:
        return self.start <= t < self.end

    def is_queued_at(self, t: int) -> bool:
        return self.schd <= t < self.start

    def is_completed_at(self, t: int) -> bool:
        return not self.will_fail and self.end <= t

    def is_failed_at(self, t: int) -> bool:
        return self.will_fail and self.end <= t

    def is_unscheduled_at(self, t: int) -> bool:
        return self.schd > t

    def copy(self) -> "Job":
        return Job(self.jid, self.cores, self.memory, self.disk, self.schd,
                   self.start, self.end, self.will_fail, self.fails, self.server)

    def current_status(self, t: int) -> str:
        if self.is_running_at(t):
            return "running"
        if self.is_queued_at(t):
            return "queued"
        if self.is_completed_at(t):
            return "completed"
        if self.is_failed_at(t):
            return "failed"
        if self.is_unscheduled_at(t):
            return "unscheduled"

    def print_job(self, t: int) -> str:
        return (
                "j{}: {},  ".format(self.jid, self.current_status(t)) +
                "cores: {},  ".format(self.cores) +
                "memory: {},  ".format(self.memory) +
                "disk: {},\n".format(self.disk) +
                "schd: {},  ".format(self.schd) +
                "start: {},  ".format(self.start) +
                "end: {},  ".format(self.end) +
                "will fail: {},  ".format(self.will_fail) +
                "fails: {},\n".format(self.fails) +
                "On server: {} {}".format(self.server.type_, self.server.sid)
        )

    def set_job_times(self, log: str, pos: int) -> None:
        with open(log, "rb") as f:
            f.seek(pos, 0)

            while True:
                line = f.readline().decode("utf-8")

                if not line:
                    break

                msg = line.split()

                if msg[1] == "JOBP" and int(msg[3]) == self.jid:
                    time = int(msg[2])
                    self.will_fail = True
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
def get_jobs(log: str, servers: "OrderedDict[str, OrderedDict[int, Server]]") -> None:
    job_failures = {}  # type: Dict[int, int]

    with open(log, "rb") as f:
        while True:
            line = f.readline()

            if b"JOB" in line:
                job_line = line.decode("utf-8").split()
                make_job(log, f.tell(), job_line, servers, job_failures)

            if not line:
                break


# noinspection PyUnresolvedReferences
def make_job(log: str, file_pos: int, msg: List[str],
             servers: "OrderedDict[str, OrderedDict[int, Server]]", job_failures: Dict[int, int]) -> Job:
    schd = int(msg[2])
    jid = int(msg[3])
    cores = int(msg[5])
    memory = int(msg[6])
    disk = int(msg[7])
    fails = 0

    if jid not in job_failures:
        job_failures[jid] = 0

    if msg[1] == "JOBP":
        job_failures[jid] += 1
        fails = job_failures[jid]

    with open(log, "rb") as f:
        f.seek(file_pos)

        while True:
            line = f.readline()

            if b"JOBP" in line:
                fail_jid = int(line.decode("utf-8").split()[3])

                if jid == fail_jid:
                    break

            if b"SCHD" in line:
                schedule = line.decode("utf-8").split()
                s_type = schedule[3]
                sid = int(schedule[4])
                server = servers[s_type][sid]

                job = Job(jid, cores, memory, disk, schd, fails=fails, server=server)
                job.set_job_times(f.name, f.tell())
                server.jobs.append(job)

                return job

            if not line:
                break


def get_job_at(jobs: List[Job], t: int) -> Job:
    # Make sure jobs are sorted by schd
    if t <= jobs[0].schd:
        return jobs[0]

    best = None
    diff = sys.maxsize

    for job in jobs:
        d = t - job.schd

        if d == 0:
            return job
        elif 0 < d < diff:
            best = job
            diff = d
    return best


def job_list_to_dict(jobs: List[Job]) -> "OrderedDict[int, Job]":
    return OrderedDict((j.jid, j) for j in jobs)
