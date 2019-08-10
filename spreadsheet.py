import csv
import os
import re
from typing import Union, Callable

from file_read_backwards import FileReadBackwards
from natsort import natsorted


class Results:
    def __init__(self, servers: int, utilisation: float, cost: float, waiting: int, execution: int, turnaround: int):
        self.servers = servers
        self.utilisation = utilisation
        self.cost = cost
        self.waiting = waiting
        self.execution = execution
        self.turnaround = turnaround


def parse_log(log: str) -> str:
    with FileReadBackwards(log, encoding="utf-8") as log_f:
        return log_f.readline().strip() + ' ' + log_f.readline().strip()


def extract(find: str, string: str, type_: Callable) -> Union[int, float]:
    return type_(re.search(find + r"(\d+\.?\d*)", string).group(1))


def make_results(log: str) -> Results:
    raw_text = parse_log(log)

    servers = extract(r"servers used: ", raw_text, int)
    util = extract(r"avg utilisation: ", raw_text, float)
    cost = extract(r"total cost: \$", raw_text, float)
    wait = extract(r"avg waiting time: ", raw_text, int)
    execute = extract(r"avg exec time: ", raw_text, int)
    turn = extract(r"avg turnaround time: ", raw_text, int)

    return Results(servers, util, cost, wait, execute, turn)


folder = "test-logs"
csv_filename = "test.csv"

print()
with open(csv_filename, 'w', newline='') as csv_f:
    writer = csv.writer(csv_f)
    writer.writerow(["failure model", "algorithm", "number of servers", "servers used", "avg utilisation",
                     "total cost", "avg waiting time", "avg exec time", "avg turnaround time"])

    for filename in natsorted(os.listdir(folder)):
        cats = re.split(r"[\-.]", filename.replace("config", ''))[:-2]
        f_model = cats[0]
        algo = cats[1]
        size = cats[2]

        res = make_results(f"./{folder}/{filename}")
        writer.writerow([f_model, algo, size, res.servers, res.utilisation,
                         res.cost, res.waiting, res.execution, res.turnaround])
