import csv
import os
import re
from argparse import ArgumentParser
from typing import Union, Callable, Dict, Tuple

from file_read_backwards import FileReadBackwards
from natsort import natsorted


class Result:
    def __init__(self, model: str, algorithm: str, size: int, servers: int, utilisation: float,
                 cost: float, waiting: int, execution: int, turnaround: int):
        self.model = model
        self.algorithm = algorithm
        self.size = size
        self.servers = servers
        self.utilisation = utilisation
        self.cost = cost
        self.waiting = waiting
        self.execution = execution
        self.turnaround = turnaround

    def to_dict(self) -> Dict[str, Union[str, int, float]]:
        return {
            "model": self.model,
            "algorithm": self.algorithm,
            "size": self.size,
            "servers used": self.servers,
            "avg utilisation": self.utilisation,
            "total cost": self.cost,
            "avg waiting time": self.waiting,
            "avg exec time": self.execution,
            "avg turnaround time": self.turnaround
        }


def sort_algorithms(string: str) -> Tuple[int, str]:
    if string in "ff bf wf":
        return 0, string
    else:
        return 1, string


def parse_log(log: str) -> str:
    with FileReadBackwards(log, encoding="utf-8") as log_f:
        return log_f.readline().strip() + ' ' + log_f.readline().strip()


def extract(find: str, string: str, type_: Callable) -> Union[int, float]:
    match = re.search(find + r"(-?\d+\.?\d*)", string)
    return type_(match.group(1))


def get_filename_info(filename: str) -> Dict[str, str]:
    res = {}
    cats = re.split(r"[\-.]", filename.replace("config", ''))[:-2]

    res["model"] = cats[0]
    res["algo"] = cats[1]
    res["size"] = cats[2]

    return res


def make_result(log: str) -> Result:
    raw_text = parse_log(log)

    servers = extract(r"servers used: ", raw_text, int)
    util = extract(r"avg utilisation: ", raw_text, float)
    cost = extract(r"total cost: \$", raw_text, float)
    wait = extract(r"avg waiting time: ", raw_text, int)
    execute = extract(r"avg exec time: ", raw_text, int)
    turn = extract(r"avg turnaround time: ", raw_text, int)

    f_info = get_filename_info(os.path.basename(log))
    model = f_info["model"]
    algo = f_info["algo"]
    size = int(f_info["size"])

    return Result(model, algo, size, servers, util, cost, wait, execute, turn)


def get_results(folder: str) -> Dict[str, Dict[str, Dict[int, Result]]]:
    result_d = {}

    for filename in os.listdir(folder):
        f_info = get_filename_info(filename)
        model = f_info["model"]
        algo = f_info["algo"]
        size = int(f_info["size"])

        if model not in result_d:
            result_d[model] = {}
        if algo not in result_d[model]:
            result_d[model][algo] = {}

        result_d[model][algo][size] = make_result("./{}/{}".format(folder, filename))

    return result_d


def get_structured_results(log: str) -> Dict[str, Dict[str, Dict[str, Dict[int, Union[str, int, float]]]]]:
    result_d = {"servers used": {}, "avg utilisation": {}, "total cost": {},
                "avg waiting time": {}, "avg turnaround time": {}}
    results = get_results(log)

    for metric in result_d:
        for model in results:
            if model not in result_d[metric]:
                result_d[metric][model] = {}

            for algorithm in results[model]:
                if algorithm not in result_d[metric][model]:
                    result_d[metric][model][algorithm] = {}

                for size in natsorted(results[model][algorithm]):
                    res = results[model][algorithm][size].to_dict()
                    result_d[metric][model][algorithm][size] = res[metric]
    return result_d


def make_spreadsheet(results: Dict[str, Dict[str, Dict[str, Dict[int, Union[str, int, float]]]]],
                     filename: str = "results.csv") -> None:
    with open(filename, 'w', newline='') as csv_f:
        writer = csv.writer(csv_f)
        sizes = list(next(iter(next(iter(next(iter(results.values())).values())).values())).keys())
        writer.writerow([''] + sizes)

        for metric, met_dict in results.items():
            writer.writerow([metric])

            for model, mod_dict in met_dict.items():
                writer.writerow([model])

                for algo in sorted(mod_dict, key=sort_algorithms):
                    writer.writerow([algo] + list(mod_dict[algo].values()))
            writer.writerow(["average"])

            for algo in sorted(mod_dict, key=sort_algorithms):
                writer.writerow([algo] + [''] * len(sizes))

            writer.writerow('')


parser = ArgumentParser(description="Generates spreadsheets from logs")
parser.add_argument("dir", help="directory of logs")
parser.add_argument("-o", "--output", default="results.csv", help="name of output file")
args = parser.parse_args()

make_spreadsheet(get_structured_results(args.dir), args.output)
