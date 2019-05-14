# https://stackoverflow.com/a/12344609/8031185

import atexit
from time import strftime, localtime, clock
from datetime import timedelta


def seconds_to_str(elapsed=None):
    if elapsed is None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))


def log(s, elapsed=None):
    line = "=" * 40
    print(line)
    print(seconds_to_str(), '-', s)
    if elapsed:
        print("Elapsed time:", elapsed)
    print(line)
    print()


def end_log():
    end = clock()
    elapsed = end - start
    log("End Program", seconds_to_str(elapsed))


start = clock()
atexit.register(end_log)
log("Start Program")
