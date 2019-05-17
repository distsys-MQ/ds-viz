# let = """\
# a
# b
# c
# """
# num = """\
# 1
# 2
# 3
# """
# res = "\n".join("".join(i) for i in zip(let.split(), num.split()))
# print(res)
width = 100


# start = 20
# end = 30
# print("[{} {} {}]".format(' ' * (start - 2), "/" * (end - start), ' ' * (width - end - 2)))
# print("[{:^{width}}]".format("/" * (end - start), width=width))


def print_server(jobs):
    res = "["
    next_starts = [i for i, _ in jobs[1:]]
    next_starts.append(width)
    res += ' ' * (jobs[0][0] - 2)

    for j, ns in zip(jobs, next_starts):
        res += '|' * int((j[1] - j[0]))
        res += ' ' * (ns - j[1])
    res += "]"

    return res


times = [(20, 30), (50, 90)]

print(print_server(times))
