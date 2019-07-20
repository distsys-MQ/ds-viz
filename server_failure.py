from typing import List, BinaryIO


class ServerFailure:
    def __init__(self, fail: int, recover: int = 0):
        self.fail = fail
        self.recover = recover


def get_failures(file: str, servers) -> List[ServerFailure]:
    failures = []

    with open(file, "rb") as f:
        while True:
            line = f.readline()

            if b"RESF" in line:
                f.seek(-len(line), 1)
                failures.append(make_failure(f, servers))

            if not line:
                break

    return failures


def make_failure(f: BinaryIO, servers) -> ServerFailure:
    msg = f.readline().decode("utf-8").split()
    kind = msg[2]
    sid = int(msg[3])
    f_time = int(msg[4])

    while True:
        line = f.readline()

        if b"RESR" in line:
            msg = line.decode("utf-8").split()

            if msg[2] == kind and int(msg[3]) == sid:
                failure = ServerFailure(f_time, int(msg[4]))
                server = servers[kind][sid]
                server.failures.append(failure)

                return failure

        if not line:
            break
