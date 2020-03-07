import csv
import os

import re


def make_spreadsheet():
    folder = "results"
    re_turn = re.compile(r".* avg turnaround time: (\d+)")

    with open("out.csv", 'w', newline='') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(["failure trace", "ff", "bf", "minwj", "csa"])
        servers = -1
        config = ""

        for filename in os.listdir(folder):
            with open("{}/{}".format(folder, filename), 'r') as log:
                title = filename.split('-')
                length = title[1]
                load = title[2]
                trace = title[3]

                new_servers = title[0].split('g')[1]
                if new_servers != servers:
                    writer.writerow([new_servers])
                    servers = new_servers

                new_config = "{}-{}".format(length, load)
                if new_config != config:
                    writer.writerow([new_config])
                    config = new_config

                times = []

                for line in log:
                    if line.startswith("# avg"):
                        turn = re_turn.match(line).group(1)
                        times.append(turn)

                writer.writerow([trace] + times)


make_spreadsheet()
