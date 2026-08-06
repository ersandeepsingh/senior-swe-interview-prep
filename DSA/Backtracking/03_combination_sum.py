# Combination Sum
#
# LeetCode: 39
# Difficulty: Medium
# Pattern: Combinations sum
#
# Problem:
# Given an array of distinct integers candidates and a target integer target, return a list
# of all unique combinations of candidates where the chosen numbers sum to target.
# You may return the combinations in any order.
#
# The same number may be chosen from candidates an unlimited number of times.
# Two combinations are unique if the frequency of at least one of the chosen numbers is different.
#
# Example 1:
# Input: candidates = [2, 3, 6, 7], target = 7
# Output: [[2, 2, 3], [7]]
#
# Example 2:
# Input: candidates = [2, 3, 5], target = 8
# Output: [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
#
# Example 3:
# Input: candidates = [2], target = 1
# Output: []
#
# Constraints:
# - 1 <= candidates.length <= 30
# - 2 <= candidates[i] <= 40
# - All elements of candidates are distinct
# - 1 <= target <= 40

from turtle import back


def combination_sum(candidates, target):
    result = []
    path = []
    
    def backtrack(index, sum):
        if sum == target:
            result.append(path.copy())
            return
        if sum > target:
                return
        for i in range(index,len(candidates)):
            #append
            path.append(candidates[i])
            #explore
            backtrack(i, sum+candidates[i])
            #undo
            val = path.pop()
    
    backtrack(0,0)
    return result

# some more optimisation

def combination_sum(candidates, target):
    result = []
    path = []
    def backtrack(start,remaining) -> None:
        if remaining == 0:
            result.append(path.copy())
            return

        for index in range(start, len(candidates)):
            value = candidates[index]

            if value > remaining:
                break

            path.append(value)
            backtrack(index, remaining - value)
            path.pop()

    backtrack(0, target)
    return result
            


if __name__ == '__main__':
    candidates = [2, 3, 6, 7]
    target = 7
    ans = combination_sum(candidates, target)
    print(ans)
