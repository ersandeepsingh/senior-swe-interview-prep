# Reorganize String
#
# LeetCode: 767
# Difficulty: Medium
# Pattern: Rearrange with constraint
#
# Problem:
# Given a string s, rearrange the characters of s so that any two adjacent characters are
# not the same.
#
# Return any possible rearrangement of s or return "" if not possible.
#
# Example 1:
# Input: s = "aab"
# Output: "aba"
#
# Example 2:
# Input: s = "aaab"
# Output: ""
#
# Constraints:
# - 1 <= s.length <= 500
# - s consists of lowercase English letters

from collections import Counter
import heapq

def reorganize_string(s):
    # Count frequency of each character
    count = Counter(s)
    max_heap = [(-freq, char) for char, freq in count.items()]
    heapq.heapify(max_heap)
    
    prev = (0, '')  # (frequency, character)
    result = []
    
    while max_heap:
        freq, char = heapq.heappop(max_heap)
        result.append(char)
        
        # If there's a previously used character to re-add (not zero freq)
        if prev[0] < 0:
            heapq.heappush(max_heap, prev)
        
        # Next prev is current one minus one freq
        prev = (freq + 1, char)  # Increase because freq is negative
    
    res_str = "".join(result)
    # Verify if the rearrangement is valid, else return ""
    for i in range(1, len(res_str)):
        if res_str[i] == res_str[i-1]:
            return ""
    return res_str


if __name__ == '__main__':
    s = "aab"
    ans = reorganize_string(s)
    print(ans)
