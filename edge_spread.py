#!/usr/bin/env python3

import csv
import os
import re
from datetime import datetime
from typing import Dict


class Video:
    def __init__(self, name: str, dash_down_time: float = 0, down_time: float = 0,
                 sum_time: float = 0, return_time: float = 0):
        self.name = name
        self.dash_down_time = dash_down_time
        self.down_time = down_time
        self.sum_time = sum_time
        self.return_time = return_time


master = "00a6a4630f4e34d8"
timestamp = r"^(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s+\d+\s+\d+ "
re_timestamp = re.compile(r"^(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})\.(\d{3})(?=\s+\d+\s+\d+).*(?:\s+)?$")
re_dash_down = re.compile(
    timestamp +
    r"W DashDownloadManager: Successfully downloaded "
    r"(.*)\.mp4 in (\d*\.?\d*)s(?:\s+)?$")
re_down = re.compile(
    timestamp +
    r"W NearbyFragment: Completed downloading "
    r"(.*)\.mp4 from Endpoint{id=\w{4}, name=(.*) \[(\w{4})\]} in (\d*\.?\d*)s(?:\s+)?$")
re_comp = re.compile(timestamp + r"W Summariser: {3}filename: (.*)\.mp4(?:\s+)?$")
re_sum = re.compile(timestamp + r"W Summariser: {3}time: (\d*\.?\d*)s(?:\s+)?$")
re_pref = re.compile(timestamp + r"W NearbyFragment: Preferences:(?:\s+)?$")

test = """06-29 01:56:05.825 21050 21050 E ViewRootImpl: sendUserActionEvent() returned.
06-29 01:57:05.124 21050 21050 W NearbyFragment: Completed downloading 20200312_150643!000.mp4 from Endpoint{id=vf39, name=Nexus 5X [34d8]} in 01.863s
06-29 01:57:07.238 21050 21050 W NearbyFragment: Completed downloading 20200312_150643!001.mp4 from Endpoint{id=vf39, name=Nexus 5X [34d8]} in 02.003s
06-29 01:57:07.478 21050 23114 W Summariser: No activity detected
06-29 01:57:07.546 21050 23114 W Summariser: Summarisation completed
06-29 01:57:07.546 21050 23114 W Summariser:   filename: 20200312_150643!000.mp4
06-29 01:57:07.546 21050 23114 W Summariser:   active sections: 0
06-29 01:57:07.546 21050 23114 W Summariser:   time: 02.211s
06-29 01:57:07.546 21050 23114 W Summariser:   original duration: 16.07
06-29 01:57:07.546 21050 23114 W Summariser:   summarised duration: -1.0
06-29 01:57:07.546 21050 23114 W Summariser:   noise tolerance: 45.00
06-29 01:57:07.546 21050 23114 W Summariser:   quality: 23
06-29 01:57:07.546 21050 23114 W Summariser:   speed: medium
06-29 01:57:07.546 21050 23114 W Summariser:   freeze duration: 1.00
06-29 01:57:09.216 21050 21050 W NearbyFragment: Completed downloading 20200312_150643!002.mp4 from Endpoint{id=vf39, name=Nexus 5X [34d8]} in 01.911s
06-29 01:57:09.691 21050 23114 W Summariser: No activity detected
06-29 01:57:09.773 21050 23114 W Summariser: Summarisation completed
06-29 01:57:09.773 21050 23114 W Summariser:   filename: 20200312_150643!001.mp4
06-29 01:57:09.773 21050 23114 W Summariser:   active sections: 0
06-29 01:57:09.773 21050 23114 W Summariser:   time: 02.128s
06-29 01:57:09.773 21050 23114 W Summariser:   original duration: 16.01
06-29 01:57:09.773 21050 23114 W Summariser:   summarised duration: -1.0
06-29 01:57:09.773 21050 23114 W Summariser:   noise tolerance: 45.00
06-29 01:57:09.773 21050 23114 W Summariser:   quality: 23
06-29 01:57:09.773 21050 23114 W Summariser:   speed: medium
06-29 01:57:09.773 21050 23114 W Summariser:   freeze duration: 1.00"""


# for line in test.splitlines():
#     res = re_down.match(line)
#
#     if res is not None:
#         print(res.group(1))


def get_video_name(name: str) -> str:
    sep = '!'
    if sep in name:
        return name.split(sep)[0]
    else:
        return name


def timestamp_to_datetime(line: str) -> datetime:
    match = re_timestamp.match(line)

    year = 2020
    month = int(match.group(1))
    day = int(match.group(2))
    hour = int(match.group(3))
    minute = int(match.group(4))
    second = int(match.group(5))
    microsecond = int(int(match.group(6)) * 1000)

    return datetime(year, month, day, hour, minute, second, microsecond)


def get_total_time(master_log_file: str):
    start = None
    end = None

    with open(master_log_file, 'r') as master_log:
        for line in master_log:
            if start is None:
                pref = re_pref.match(line)

                if pref is not None:
                    start = line
            down_match = re_down.match(line)
            comp_match = re_comp.match(line)

            if down_match is not None:
                end = line
            elif comp_match is not None:
                end = line
    return timestamp_to_datetime(end) - timestamp_to_datetime(start)


def parse_master_log(master_filename: str, log_dir: str) -> Dict[str, Video]:
    videos = {}  # type: Dict[str, Video]

    with open("{}/{}".format(log_dir, master_filename), 'r') as master_log:
        for line in master_log:
            dash_down = re_dash_down.match(line)
            down = re_down.match(line)

            if dash_down is not None:
                video_name = get_video_name(dash_down.group(2))
                dash_down_time = float(dash_down.group(3))

                video = Video(name=video_name, dash_down_time=dash_down_time)
                videos[video_name] = video

            if down is not None:
                video_name = get_video_name(down.group(2))
                return_time = float(down.group(5))

                videos[video_name].return_time += return_time
    return videos


def parse_worker_logs(videos: Dict[str, Video], log_dir: str) -> Dict[str, Dict[str, Video]]:
    worker_logs = [log for log in os.listdir(log_dir) if log.endswith(".log") and master not in log]
    # Initialise device dictionary with empty dictionaries
    devices = {device[-8:-4]: {} for device in worker_logs}

    for filename in worker_logs:
        with open("{}/{}".format(log_dir, filename), 'r') as work_log:
            device_name = filename[-8:-4]

            for line in work_log:
                down = re_down.match(line)
                comp = re_comp.match(line)

                if down is not None:
                    video_name = get_video_name(down.group(2))
                    down_time = float(down.group(5))

                    video = videos[video_name]
                    video.down_time += down_time
                    devices[device_name][video_name] = video
                elif comp is not None:
                    video_name = get_video_name(comp.group(2))
                    work_log.readline()  # skip active sections line
                    time_line = work_log.readline()
                    sum_time = float(re_sum.match(time_line).group(2))

                    videos[video_name].sum_time += sum_time
    return devices


def make_offline_spreadsheet(log_dir: str = "offline", out_name: str = "out.csv"):
    offline_logs = [log for log in os.listdir(log_dir) if log.endswith(".log")]

    with open(out_name, 'w', newline='') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(["Offline simulations"])

        for filename in offline_logs:
            with open("{}/{}".format(log_dir, filename), 'r') as offline_log:
                writer.writerow([filename[-8:-4]])
                writer.writerow(["Filename", "Download time (s)", "Summarisation time (s)"])
                videos = {}  # type: Dict[str, Video]

                for line in offline_log:
                    dash_down = re_dash_down.match(line)
                    comp = re_comp.match(line)

                    if dash_down is not None:
                        video_name = get_video_name(dash_down.group(2))
                        dash_down_time = float(dash_down.group(3))

                        videos[video_name] = Video(name=video_name, dash_down_time=dash_down_time)

                    if comp is not None:
                        video_name = get_video_name(comp.group(2))
                        offline_log.readline()  # skip active sections line
                        time_line = offline_log.readline()
                        sum_time = float(re_sum.match(time_line).group(2))

                        videos[video_name].sum_time = sum_time

                for video in videos.values():
                    writer.writerow([video.name, video.dash_down_time, video.sum_time])


def make_spreadsheet(devices: Dict[str, Dict[str, Video]], master_filename: str, log_dir: str, out: str = "out.csv"):
    master_path = "{}/{}".format(log_dir, master_filename)

    with open(master_path, 'r') as master_log:
        for line in master_log:
            pref = re_pref.match(line)

            if pref is not None:
                master_log.readline()  # skip auto download line
                algo = master_log.readline().split()[-1]
                fast = master_log.readline().split()[-1] == "true"
                seg = master_log.readline().split()[-1] == "true"
                master_log.readline()  # skip auto segmentation line
                seg_num = int(master_log.readline().split()[-1]) if seg else 1

    with open(out, 'w', newline='') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow([
            "Fast scheduling" if fast else "Non-fast scheduling",
            "Segments: {}".format(seg_num),
            "Nodes: {}".format(len([log for log in os.listdir(log_dir) if log.endswith(".log")])),
            "Algorithm: {}".format(algo),
            "Master: {}".format(master_filename[-8:-4]),
        ])

        for device_name, video_dict in devices.items():
            writer.writerow([
                "Device: {}".format(device_name),
                "Dir: {}".format(log_dir)
            ])
            writer.writerow([
                "Filename",
                "Download Time (s)",
                "Transfer time (s)",
                "Return time (s)",
                "Summarisation time (s)"
            ])

            for video in video_dict.values():
                writer.writerow([
                    video.name,
                    "{:.3f}".format(video.dash_down_time),
                    "{:.3f}".format(video.down_time),
                    "{:.3f}".format(video.return_time) if video.return_time != 0 else "n/a",
                    "{:.3f}".format(video.sum_time)
                ])

        time = get_total_time(master_path)
        writer.writerow(["Actual total time", time])


def edge_spread(log_dir: str):
    master_filename = "{}.log".format(master)
    videos = parse_master_log(master_filename, log_dir)
    devices = parse_worker_logs(videos, log_dir)
    make_spreadsheet(devices, master_filename, log_dir)


edge_spread("./fast/segmented/node2/20200629_015535")
# TODO add command-line argument parsing
