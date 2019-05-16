import timing

let = """\
a
b
c
"""

num = """\
1
2
3
"""
# res = ""
# for a, b in zip(let.split(), num.split()):
#     res += a + b + "\n"
# print(res)

# res = []
# for a, b in zip(let.split(), num.split()):
#     res.append(a + b + "\n")
# res = "".join(res)
# print(res)

# res = []
# for a, b in zip(let.split(), num.split()):
#     res.append(f"{a}{b}\n")
# res = "".join(res)
# print(res)

res = "\n".join("".join(i) for i in zip(let.split(), num.split()))
# res = "".join(res)
print(res)
