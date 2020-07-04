#!/usr/bin/env python3

import csv
import os
import re
from datetime import datetime
from typing import Dict


class Video:
    def __init__(self, name: str, dash_down_time: float = None, down_time: float = None,
                 sum_time: float = None, return_time: float = None):
        self.name = name
        self.dash_down_time = dash_down_time
        self.down_time = down_time
        self.sum_time = sum_time
        self.return_time = return_time


master = "00a6a4630f4e34d8"
timestamp = r"^(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \s+\d+\s+\d+ "
re_timestamp = re.compile(r"^(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})\.(\d{3}) (?=\s+\d+\s+\d+).*(?:\s+)?$")
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
re_algo = re.compile(timestamp + r"W NearbyFragment: {3}Algorithm: (.*)(?:\s+)?$")

test = """06-29 01:16:44.208  5434  5434 E TransferService: No notification is passed in the intent. Unable to transition to foreground.
06-29 01:16:57.319  5434  5434 W NearbyFragment: Preferences:
06-29 01:16:57.319  5434  5434 W NearbyFragment:   Auto download: true
06-29 01:16:57.319  5434  5434 W NearbyFragment:   Algorithm: best
06-29 01:16:57.319  5434  5434 W NearbyFragment:   Fast scheduling: true
06-29 01:16:57.319  5434  5434 W NearbyFragment:   Segmentation: false
06-29 01:16:57.319  5434  5434 W NearbyFragment:   Auto segmentation: false
06-29 01:16:57.319  5434  5434 W NearbyFragment:   Segment number: 4
06-29 01:16:57.319  5434  5434 W NearbyFragment:   Noise tolerance: 45.00
06-29 01:16:57.319  5434  5434 W NearbyFragment:   Quality: 23
06-29 01:16:57.319  5434  5434 W NearbyFragment:   Speed: medium
06-29 01:16:57.319  5434  5434 W NearbyFragment:   Freeze duration: 1.00
06-29 01:16:57.320  5434  5434 W NearbyFragment: Download delay: 1s
06-29 01:16:57.320  5434  5434 W NearbyFragment: Started downloading from dashcam"""


# for line in test.splitlines():
#     res = re_pref.match(line)
#
#     if res is not None:
#         print(res.group(1))


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
                video_name = dash_down.group(2)
                dash_down_time = float(dash_down.group(3))

                video = Video(name=video_name, dash_down_time=dash_down_time)
                videos[video_name] = video

            if down is not None:
                video_name = down.group(2)
                return_time = float(down.group(5))

                videos[video_name].return_time = return_time
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
                    video_name = down.group(2)
                    down_time = float(down.group(5))

                    video = videos[video_name]
                    video.down_time = down_time
                    devices[device_name][video_name] = video
                elif comp is not None:
                    video_name = comp.group(2)
                    work_log.readline()  # skip active sections line
                    time_line = work_log.readline()
                    sum_time = float(re_sum.match(time_line).group(2))

                    videos[video_name].sum_time = sum_time
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
                        video_name = dash_down.group(2)
                        dash_down_time = float(dash_down.group(3))

                        videos[video_name] = Video(name=video_name, dash_down_time=dash_down_time)

                    if comp is not None:
                        video_name = comp.group(2)
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
                algo_line = master_log.readline()
                algo = re_algo.match(algo_line).group(2)

    with open(out, 'w', newline='') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(["{} ({} - {})".format(log_dir, master_filename[-8:-4], algo)])

        for device_name, video_dict in devices.items():
            writer.writerow([device_name])
            writer.writerow(["Filename", "Download Time (s)", "Transfer time (s)",
                             "Return time (s)", "Summarisation time (s)"])

            for video in video_dict.values():
                writer.writerow([video.name, video.dash_down_time, video.down_time, video.return_time, video.sum_time])

        time = get_total_time(master_path)
        writer.writerow([time])


def edge_spread(log_dir: str):
    master_filename = "{}.log".format(master)
    videos = parse_master_log(master_filename, log_dir)
    devices = parse_worker_logs(videos, log_dir)
    make_spreadsheet(devices, master_filename, log_dir)


edge_spread("./fast/non-segmented/node2/20200629_014054")
