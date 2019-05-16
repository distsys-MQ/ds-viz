import textwrap

# user = "Username"
# prefix = user + ":  "
# expanded_indent = textwrap.fill(prefix+'$', replace_whitespace=False)[:-1]
# subsequent_indent = ' ' * len(expanded_indent)
# wrapper = textwrap.TextWrapper(initial_indent=prefix,
#                                subsequent_indent=subsequent_indent)
# message = "LEFTLEFTLEFTLEFTLEFTLEFTLEFT RIGHTRIGHTRIGHT " * 3
# test = wrapper.fill(message)
# print(test)

job = "j0"
prefix = job + ":\n  "
expanded_indent = textwrap.fill(prefix+'$', replace_whitespace=False)
subsequent_indent = ' ' * len(expanded_indent)
wrapper = textwrap.TextWrapper(initial_indent=prefix,
                               subsequent_indent=subsequent_indent)
# message = """\
# j0 s143 e19466
# j3 s19466 e19708
# j4 s19708 e24285
# j9 s24285 e104842
# """
message = "s143 e19466"
test = wrapper.fill(message)
print(test)

# msg = "j0 s143 e19466" \
#       "j3 s19466 e19708" \
#       "j4 s19708 e24285" \
#       "j9 s24285 e104842"
