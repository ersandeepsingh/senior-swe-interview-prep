# Partition Labels
#
# LeetCode: 763
# Difficulty: Medium
# Pattern: Partition labels
#
# Problem:
# You are given a string s. We want to partition the string into as many parts as possible
# so that each letter appears in at most one part. For example, the string "ababcc" can be
# partitioned into ["abab", "cc"], but not into ["aba", "bcc"] since the letter 'b' appears
# in both parts.
#
# Note that the partition is done so that after concatenating all the parts in order, the
# resultant string should be s.
#
# Return a list of integers representing the size of these parts.
#
# Example 1:
# Input: s = "ababcbacadefegdehijhklij"
# Output: [9, 7, 8]
#
# Example 2:
# Input: s = "eccbbbbdec"
# Output: [10]
#
# Constraints:
# - 1 <= s.length <= 500
# - s consists of lowercase English letters

def partition_labels(s):
    # Hint: First, record the last index where each character appears in the string.
    # Then, iterate through the string, expanding the current partition to the farthest last occurrence of any character seen so far.
    # When your iteration index reaches the current partition's end, you can finalize the partition and start a new one.
    index = {}
    for i in range(len(s)):
        index[s[i]] = i
    left = 0
    right = 0
    result =[]
    while left<len(s):
        right = index[s[left]]
        start = left
        while left<right:
            if index[s[left]]>right:
                right = index[s[left]]
            left += 1
        result.append(right-start+1)
        left = right+1
    return result

# More cleaner
def partition_labels(s):
    # It tracks the last occurrence of each character, and greedily expands partitions to cover 
    # the farthest last occurrence of any character seen so far.

    # First, find the last occurrence index for each character in s.
    last_index = {ch: i for i, ch in enumerate(s)}

    result = []
    start, end = 0, 0

    for i, ch in enumerate(s):
        end = max(end, last_index[ch])  # Always expand the partition end to the farthest seen so far.
        if i == end:
            # Current partition ends here
            result.append(end - start + 1)
            start = i + 1
            
    return result

if __name__ == '__main__':
    s = "ababcc"
    ans = partition_labels(s)
    print(ans)
