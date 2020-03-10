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


def parse_worker_logs(log_dir: str) -> Dict[str, Dict[str, Video]]:
    worker_logs = [log for log in os.listdir(log_dir) if log.startswith("worker")]
    # Initialise device dictionary with empty dictionaries
    devices = {device[:-4]: {} for device in worker_logs}

    for filename in worker_logs:
        with open("{}/{}".format(log_dir, filename), 'r') as work_log:
            device_name = filename[:-4]

            for line in work_log:
                down = re_down.match(line)
                comp = re_comp.match(line)

                if down is not None:
                    video_name = down.group(1)
                    down_time = float(down.group(2))

                    video = Video(name=video_name, down_time=down_time)
                    devices[device_name][video_name] = video
                elif comp is not None:
                    video_name = comp.group(1)
                    time_line = work_log.readline()
                    sum_time = float(re_sum.match(time_line).group(1))

                    devices[device_name][video_name].sum_time = sum_time

    return devices


def parse_master_log(devices: Dict[str, Dict[str, Video]], master_filename: str, log_dir: str):
    with open("{}/{}".format(log_dir, master_filename), 'r') as master_log:
        for line in master_log:
            down = re_down.match(line)

            if down is not None:
                video_name = down.group(1)
                return_time = float(down.group(2))

                # FIXME add device name to download log messages, should replace human-readable device names
                #  with model-SN format
                for video_dict in devices.values():
                    if video_name in video_dict:
                        video_dict[video_name].return_time = return_time


def make_offline_spreadsheet(log_dir: str = "offline", out_name: str = "out.csv"):
    offline_logs = [log for log in os.listdir(log_dir) if log.startswith("offline")]

    with open(out_name, 'w', newline='') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(["Offline simulations"])

        for filename in offline_logs:
            with open("{}/{}".format(log_dir, filename), 'r') as offline_log:
                writer.writerow([filename[:-4]])
                writer.writerow(["Filename", "Summarisation time (s)"])

                for line in offline_log:
                    comp = re_comp.match(line)

                    if comp is not None:
                        video_name = comp.group(1)
                        time_line = offline_log.readline()
                        sum_time = float(re_sum.match(time_line).group(1))
                        writer.writerow([video_name, sum_time])


def make_spreadsheet(devices: Dict[str, Dict[str, Video]], master_name: str, log_dir: str, out_name: str = "out.csv"):
    with open(out_name, 'w', newline='') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(["{} ({})".format(log_dir, master_name)])

        for device_name, video_dict in devices.items():
            writer.writerow([device_name])
            writer.writerow(["Filename", "Transfer time (s)", "Return time (s)", "Summarisation time (s)"])

            for video in video_dict.values():
                writer.writerow([video.name, video.down_time, video.return_time, video.sum_time])


def edge_spread(log_dir: str):
    devices = parse_worker_logs(log_dir)
    # Each simulation log folder should contain only one master log
    master_filename = [log for log in os.listdir(log_dir) if log.startswith("master")][0]
    parse_master_log(devices, master_filename, log_dir)
    make_spreadsheet(devices, master_filename[:-4], log_dir)


edge_spread("node4")
