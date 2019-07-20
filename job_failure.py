class JobFailure:
    def __init__(self, reschd: int, start: int = None, s_kind: str = None, sid: int = None):
        self.reschd = reschd
        self.start = start
        self.s_kind = s_kind
        self.sid = sid
