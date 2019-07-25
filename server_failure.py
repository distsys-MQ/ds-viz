from typing import List, Dict


class ServerFailure:
    def __init__(self, fail: int, recover: int = None):
        self.fail = fail
        self.recover = recover


def get_failures(log: str, servers, last_time: int) -> List[ServerFailure]:
    failures = []

    with open(log, "rb") as f:
        while True:
            line = f.readline()

            if b"RESF" in line:
                failures.append(make_failure(f.name, f.tell() - len(line), servers))

            if not line:
                break

    for f in failures:
        if f.recover is None:
            f.recover = last_time

    return failures


# noinspection PyUnresolvedReferences
def make_failure(log: str, pos: int, servers: Dict[str, Dict[int, "Server"]]) -> ServerFailure:
    with open(log, "rb") as f:
        f.seek(pos, 0)

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
                failure = ServerFailure(f_time)
                server = servers[kind][sid]
                server.failures.append(failure)

                return failure
