import csv
import os

import re

re_algo = re.compile(r">+ (.*) <+")
re_cost = re.compile(r".* total cost: \$(\d+\.?\d*)")
re_turn = re.compile(r".* avg turnaround time: (\d+)")

folder = "results"

with open("out.csv", 'w', newline='') as csv_f:
    writer = csv.writer(csv_f)

    for filename in os.listdir(folder):
        with open("{}/{}".format(folder, filename), 'r') as log:
            title = filename.split('-')
            conf = title[0]
            load = "{}-{}".format(title[1], title[2])
            model = title[3]

            writer.writerow([conf, load, model])

            for line in log:
                if line[0] == '>':
                    algo = re_algo.match(line).group(1)
                elif line.startswith("# total"):
                    cost = re_cost.match(line).group(1)
                elif line.startswith("# avg"):
                    turn = re_turn.match(line).group(1)
                    writer.writerow([algo, cost, turn])
