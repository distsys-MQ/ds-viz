import timing
from server import get_servers

WIDTH = 80

servers = get_servers()

for s in servers:
    print(f"{s.kind} {s.sid}")
    print()
    for j in s.jobs:
        print(f"j{j.jid} s{j.start} e{j.end}", end=" ")
    print()
    print("|\n" * s.cores)
    print("=" * WIDTH)


# https://stackoverflow.com/q/20756516/8031185
# https://stackoverflow.com/a/47614884/8031185
# https://stackoverflow.com/q/35381065/8031185
