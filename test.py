step = 10

nums = [i for i in range(100)]
sums = [sum(nums[i * step:i * step + step]) for i in range(step)]
print(max(sums))
