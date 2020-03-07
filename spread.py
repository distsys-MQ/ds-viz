import csv
import os

import re
from functools import total_ordering


@total_ordering
class Config:
    loads = ["low", "med", "high"]

    def __init__(self, filename: str):
        self.filename = filename

        config = self.filename.split('-')
        self.servers = int(config[0].split('g')[1])
        self.length = config[1]
        self.load = config[2]
        self.load_index = Config.loads.index(self.load)
        self.trace = config[3]

    def __str__(self):
        return self.filename

    def __repr__(self):
        return self.filename

    def __lt__(self, other: "Config"):
        if self.servers != other.servers:
            return self.servers < other.servers
        if self.load_index != other.load_index:
            return self.load_index < other.load_index
        if self.length != other.length:
            return self.length > other.length
        return self.trace < other.trace

    def __le__(self, other: "Config"):
        if self.servers != other.servers:
            return self.servers < other.servers
        if self.load_index != other.load_index:
            return self.load_index < other.load_index
        if self.length != other.length:
            return self.length > other.length
        return self.trace <= other.trace

    def __eq__(self, other: "Config"):
        return self.filename == other.filename

    def __ne__(self, other: "Config"):
        return self.filename != other.filename

    def __gt__(self, other: "Config"):
        if self.servers != other.servers:
            return self.servers > other.servers
        if self.load_index != other.load_index:
            return self.load_index > other.load_index
        if self.length != other.length:
            return self.length < other.length
        return self.trace > other.trace

    def __ge__(self, other: "Config"):
        if self.servers != other.servers:
            return self.servers > other.servers
        if self.load_index != other.load_index:
            return self.load_index > other.load_index
        if self.length != other.length:
            return self.length < other.length
        return self.trace >= other.trace


def make_spreadsheet():
    folder = "results"
    re_turn = re.compile(r".* avg turnaround time: (\d+)")

    with open("out.csv", 'w', newline='') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(["failure trace", "ff", "bf", "minwj", "csa"])
        last_servers = -1
        last_length_load = ""
        # for config in sorted([Config(filename) for filename in os.listdir("results")],
        #                      key=lambda c: (c.servers, c., x[1])):
        for config in sorted([Config(filename) for filename in os.listdir("results")]):
            with open("{}/{}".format(folder, config.filename), 'r') as log:
                if config.servers != last_servers:
                    writer.writerow([config.servers])
                    last_servers = config.servers

                length_load = "{} jobs -- {} load".format(config.length, config.load)
                if length_load != last_length_load:
                    writer.writerow([length_load])
                    last_length_load = length_load

                times = []

                for line in log:
                    if line.startswith("# avg"):
                        turn = re_turn.match(line).group(1)
                        times.append(turn)

                writer.writerow([config.trace] + times)


make_spreadsheet()
