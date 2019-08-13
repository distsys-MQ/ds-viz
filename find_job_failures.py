import sys
from typing import Dict

import numpy as np


class Job:
    def __init__(self, jid: int = None):
        self.jid = jid
        self.failures = 0


def get_jobs(log: str) -> Dict[int, Job]:
    jobs = {}

    with open(log, "rb") as f:
        while True:
            line = f.readline()

            if b"JOB" in line:
                msg = line.decode("utf-8").split()
                cmd = msg[1]
                jid = int(msg[3])

                if cmd == "JOBN":
                    jobs[jid] = Job(jid)
                elif cmd == "JOBF":
                    jobs[jid].failures += 1

            if not line:
                break

    return jobs


def print_failures(jobs: Dict[int, Job]):
    for i, j in jobs.items():
        print("Job {:4}: {} failures".format(i, j.failures))


result = get_jobs(sys.argv[1])
# result = get_jobs("config100.xml.your.log")
failure_counts = [j.failures for j in result.values()]
recurrence_counts = [f for f in failure_counts if f != 0]
failed_job_count = len(recurrence_counts)

arr = np.array(recurrence_counts)

unique, counts = np.unique(arr, return_counts=True)
recurrence_counts = dict(zip(unique, counts))
recurrence_counts = {k: int(v) for k, v in recurrence_counts.items()}

# print(recurrence_counts)

for i in range(1, max(recurrence_counts.keys())):
    if i not in recurrence_counts.keys():
        recurrence_counts[i] = 0


# recurrence_counts = [i for _, i in sorted(recurrence_counts.items())]


def print_dict(d):
    for count, frequency in sorted(d.items()):
        print("{}, {}".format(count, frequency))


print_dict(recurrence_counts)
