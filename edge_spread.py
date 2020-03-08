import csv
import os
import re

folder = "node4"

re_down = re.compile(r".* Completed downloading (.*)\.mp4 in (\d*\.?\d*)s")
re_comp = re.compile(r".* filename:.*/(.*)\.mp4")
re_sum = re.compile(r".* time: (\d*\.?\d*)s")

with open("out.csv", 'w', newline='') as csv_f:
    writer = csv.writer(csv_f)
    download_times = {}

    for filename in os.listdir(folder):
        with open("{}/{}".format(folder, filename), 'r') as log:
            writer.writerow([filename])

            for line in log:
                down = re_down.match(line)
                comp = re_comp.match(line)

                if down:
                    video_name = down.group(1)
                    down_time = float(down.group(2))
                    download_times[video_name] = down_time
                elif comp:
                    video_name = comp.group(1)
                    down_time = download_times[video_name]
                    line = log.readline()
                    sum_time = float(re_sum.match(line).group(1))

                    writer.writerow([video_name, down_time, sum_time])
