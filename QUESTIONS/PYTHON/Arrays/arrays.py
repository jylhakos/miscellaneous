# $ python3 arrays.py

import numpy as np

def longest(s):
    maxLen = 1
    if s == '':
        return 0
    for i in range(len(s)):
        substring = s[i]
        for j in range(i+1, len(s)):
            if s[j] not in substring:
                substring = substring + s[j]
                maxLen = max(maxLen, len(substring))
            else:
                break
    return maxLen

def closest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

array = np.array([-4, -2, 1, 4, 8])

print(closest(array, value=0))

s = "abcabcbb"

print(longest(s))