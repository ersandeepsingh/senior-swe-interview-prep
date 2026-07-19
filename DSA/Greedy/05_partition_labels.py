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
    pass


if __name__ == '__main__':
    s = "ababcbacadefegdehijhklij"
    ans = partition_labels(s)
    print(ans)
