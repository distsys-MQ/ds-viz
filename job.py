from typing import Dict, List, BinaryIO

from job_failure import JobFailure


class Job:
    def __init__(self, jid: int, cores: int, schd: int = None, start: int = None, end: int = None,
                 failures: List[JobFailure] = None):
        self.jid = jid
        self.cores = cores
        self.schd = schd
        self.start = start
        self.end = end
        self.fail_count = 0

        if failures is None:
            self.failures = []
        else:
            self.failures = failures


def get_jobs(file: str, servers) -> List[Job]:
    jobs = []

    with open(file, "rb") as f:
        while True:
            line = f.readline()

            if b"JOBN" in line:
                f.seek(-len(line), 1)
                jobs.append(make_job(f, servers))

            if b"JOBF" in line:
                f.seek(-len(line), 1)
                add_failure(f, jobs)

            if not line:
                break

    get_job_times(file, job_list_to_dict(jobs))
    return jobs


def make_job(f: BinaryIO, servers) -> Job:
    msg = f.readline().decode("utf-8").split()
    cores = int(msg[5])

    while True:
        line = f.readline()

        if b"SCHD" in line:
            msg = line.decode("utf-8").split()
            job = Job(int(msg[2]), cores)
            server = servers[msg[3]][int(msg[4])]
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
                job = jobs[jid]

                if jid == 1831:
                    print("test")

                # TODO try replacing with a dictionary
                #  https://docs.quantifiedcode.com/python-anti-patterns/readability/not_using_if_to_switch.html
                if "SCHEDULED" in msg and job.schd is None:
                    job.schd = time
                elif "RUNNING" in msg:
                    if job.start is None:
                        job.start = time

                        jf = next((f for f in job.failures if f.start == -1), None)
                        if jf:
                            jf.start = time
                    else:
                        job.failures[job.fail_count].start = time
                        job.fail_count += 1
                elif "COMPLETED" in msg and job.end is None:
                    job.end = time


def add_failure(f: BinaryIO, jobs: List[Job]):
    msg = f.readline().decode("utf-8").split()
    jid = int(msg[3])
    time = int(msg[2])
    job = next((j for j in jobs if j.jid == jid))

    if job.start is None:
        start = -1
    else:
        start = None

    while True:
        line = f.readline()

        if b"SCHD" in line:
            msg = line.decode("utf-8").split()

            jf = JobFailure(time, start, msg[3], int(msg[4]))
            job.failures.append(jf)
            return

        if not line:
            break
