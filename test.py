import timing

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
start = 20
end = 30
# print("[{} {} {}]".format(' ' * (start - 2), "/" * (end - start), ' ' * (width - end - 2)))
print("[{:^{width}}]".format("/" * (end - start), width=width))
