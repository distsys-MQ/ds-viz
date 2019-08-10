import csv
import os
import re
from typing import Union, Callable, Dict

from file_read_backwards import FileReadBackwards
from natsort import natsorted


class Result:
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


def make_result(log: str) -> Result:
    raw_text = parse_log(log)

    servers = extract(r"servers used: ", raw_text, int)
    util = extract(r"avg utilisation: ", raw_text, float)
    cost = extract(r"total cost: \$", raw_text, float)
    wait = extract(r"avg waiting time: ", raw_text, int)
    execute = extract(r"avg exec time: ", raw_text, int)
    turn = extract(r"avg turnaround time: ", raw_text, int)

    return Result(servers, util, cost, wait, execute, turn)


def get_results(folder: str) -> Dict[str, Dict[str, Dict[int, Result]]]:
    result_d = {}

    for filename in os.listdir(folder):
        cats = re.split(r"[\-.]", filename.replace("config", ''))[:-2]
        f_model = cats[0]
        algo = cats[1]
        size = int(cats[2])

        if f_model not in result_d:
            result_d[f_model] = {}
        if algo not in result_d[f_model]:
            result_d[f_model][algo] = {}

        result_d[f_model][algo][size] = make_result(f"./{folder}/{filename}")

    return result_d


def make_spreadsheet(results: Dict[str, Dict[str, Dict[int, Result]]], filename: str = "results.csv") -> None:
    with open(filename, 'w', newline='') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(["number of servers", "servers used", "avg utilisation", "total cost",
                         "avg waiting time", "avg exec time", "avg turnaround time"])

        for model, m_dict in results.items():
            writer.writerow([model])

            for algo, algo_dict in m_dict.items():
                writer.writerow([algo])

                for size, res in natsorted(algo_dict.items()):
                    writer.writerow([size, res.servers, res.utilisation,
                                     res.cost, res.waiting, res.execution, res.turnaround])


make_spreadsheet(get_results("test-logs"))
