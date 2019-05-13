from job import get_jobs
from server import get_servers, server_list_to_dict

WIDTH = 80

servers = get_servers()
server_dict = server_list_to_dict(servers)
jobs = get_jobs()

for s in servers:
    print(f"{s.kind} {s.sid}")
    print()
    print("|\n" * s.cores)
    print("=" * WIDTH)
