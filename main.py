from server import get_servers

servers = get_servers()
WIDTH = 80

for s in servers:
    print(f"{s.kind} {s.sid}")
    print()
    print("|\n" * s.cores)
    print("=" * WIDTH)
