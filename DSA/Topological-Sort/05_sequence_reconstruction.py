# Sequence Reconstruction
#
# LeetCode: 444
# Difficulty: Medium
# Pattern: Sequence reconstruction
#
# Problem:
# You are given an integer array nums of length n where nums is a permutation of the integers
# in the range [1, n]. You are also given a 2D integer array sequences where sequences[i] is
# a subsequence of nums.
#
# Check if nums is the shortest possible and the only shortest common supersequence. The
# shortest common supersequence of sequences is the shortest sequence such that all sequences
# in sequences are subsequences of it.
#
# Return True if nums is the only shortest common supersequence of sequences. Otherwise,
# return False.
#
# Example 1:
# Input: nums = [1, 2, 3], sequences = [[1, 2], [1, 3]]
# Output: False
#
# Example 2:
# Input: nums = [1, 2, 3], sequences = [[1, 2]]
# Output: False
#
# Example 3:
# Input: nums = [1, 2, 3], sequences = [[1, 2], [1, 3], [2, 3]]
# Output: True
#
# Constraints:
# - n == nums.length
# - 1 <= n <= 10^4
# - nums is a permutation of all the integers in the range [1, n]
# - 1 <= sequences.length <= 10^4
# - 1 <= sequences[i].length <= 10^4
# - 1 <= sum(sequences[i].length) <= 10^5
# - 1 <= sequences[i][j] <= n
# - All the arrays of sequences are unique
# - sequences[i] is a subsequence of nums

def sequence_reconstruction(nums, sequences):
    pass


if __name__ == '__main__':
    nums = [1, 2, 3]
    sequences = [[1, 2], [1, 3], [2, 3]]
    ans = sequence_reconstruction(nums, sequences)
    print(ans)
