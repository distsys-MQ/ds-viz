from server import get_servers

WIDTH = 80

servers = get_servers()

for s in servers:
    print(f"{s.kind} {s.sid}")
    print()
    for j in s.jobs:
        print(f"j{j.jid}", end=" ")
    print()
    print("|\n" * s.cores)
    print("=" * WIDTH)
