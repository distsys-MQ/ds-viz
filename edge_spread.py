import csv
import os
import re
from typing import Dict


class Video:
    def __init__(self, name: str, down_time: float = None, sum_time: float = None, return_time: float = None):
        self.name = name
        self.down_time = down_time
        self.sum_time = sum_time
        self.return_time = return_time


re_down = re.compile(r".* Completed downloading (.*)\.mp4 in (\d*\.?\d*)s")
re_comp = re.compile(r".* filename:.*/(.*)\.mp4")
re_sum = re.compile(r".* time: (\d*\.?\d*)s")


def make_spreadsheet():
    folder = "node4"

    all_logs = [log for log in os.listdir(folder) if log.endswith(".log")]
    worker_logs = [log for log in all_logs if log.startswith("worker")]
    offline_logs = [log for log in all_logs if log.startswith("offline")]

    # Each simulation log folder should contain only one master log
    master_log_name = [log for log in all_logs if log.startswith("master")][0]

    # Fill dictionary of device names with empty dictionaries
    devices = {device[:-4]: {} for device in worker_logs}  # type: Dict[str, Dict[str, Video]]

    for filename in worker_logs:
        with open("{}/{}".format(folder, filename), 'r') as work_log:
            device_name = filename[:-4]

            for line in work_log:
                down = re_down.match(line)
                comp = re_comp.match(line)

                if down:
                    video_name = down.group(1)
                    down_time = float(down.group(2))

                    video = Video(name=video_name, down_time=down_time)
                    devices[device_name][video_name] = video
                elif comp:
                    video_name = comp.group(1)
                    line = work_log.readline()
                    sum_time = float(re_sum.match(line).group(1))

                    devices[device_name][video_name].sum_time = sum_time

    with open("{}/{}".format(folder, master_log_name), 'r') as master_log:
        for line in master_log:
            down = re_down.match(line)

            if down:
                video_name = down.group(1)
                return_time = float(down.group(2))

                # FIXME add device name to download log messages, should replace human-readable device names
                #  with model-SN format
                for video_dict in devices.values():
                    if video_name in video_dict:
                        video_dict[video_name].return_time = return_time

    with open("out.csv", 'w', newline='') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(["{} ({})".format(folder, master_log_name)])

        for device_name, video_dict in devices.items():
            writer.writerow([device_name])
            writer.writerow(["Filename", "Transfer time (s)", "Return time (s)", "Summarisation time (s)"])

            for video in video_dict.values():
                writer.writerow([video.name, video.down_time, video.return_time, video.sum_time])


make_spreadsheet()
