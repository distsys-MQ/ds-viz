from enum import Enum


class ServerState(Enum):
    inactive = 0
    booting = 1
    idle = 2
    active = 3
    unavailable = 4
