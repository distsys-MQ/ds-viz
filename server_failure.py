from typing import List


class ServerFailure:
    def __init__(self, fail: int, recover: int = None):
        self.fail = fail
        self.recover = recover


# noinspection PyUnresolvedReferences
def get_failures_from_resources(resource_failures: str, servers: "OrderedDict[str, OrderedDict[int, Server]]") -> None:
    with open(resource_failures) as f:
        next(f)  # Skip first line

        for line in f:
            msg = line.split()
            fail = int(msg[0])
            recover = int(msg[1])
            type_ = msg[2]
            sid = int(msg[3])

            failure = ServerFailure(fail, recover)
            servers[type_][sid].failures.append(failure)


# noinspection PyUnresolvedReferences
def get_failures(log: str, servers: "OrderedDict[str, OrderedDict[int, Server]]", end_time: int) \
        -> List[ServerFailure]:
    failures = []  # type: List[ServerFailure]

    with open(log, "rb") as f:
        while True:
            line = f.readline()

            if b"RESF" in line:
                failures.append(make_failure(f.name, f.tell() - len(line), servers))

            if not line:
                break

    for f in failures:
        if f.recover is None:
            f.recover = end_time

    return failures


# noinspection PyUnresolvedReferences
def make_failure(log: str, pos: int, servers: "OrderedDict[str, OrderedDict[int, Server]]") -> ServerFailure:
    with open(log, "rb") as f:
        f.seek(pos, 0)

        msg = f.readline().decode("utf-8").split()
        type_ = msg[2]
        sid = int(msg[3])
        f_time = int(msg[4])

        while True:
            line = f.readline()

            if b"RESR" in line:
                msg = line.decode("utf-8").split()

                if msg[2] == type_ and int(msg[3]) == sid:
                    failure = ServerFailure(f_time, int(msg[4]))
                    server = servers[type_][sid]
                    server.failures.append(failure)

                    return failure

            if not line:
                failure = ServerFailure(f_time)
                server = servers[type_][sid]
                server.failures.append(failure)

                return failure
