# Combination Sum II
#
# Problem Statement:
# Given a collection of candidate numbers (candidates) and a target number (target), 
# find all unique combinations in candidates where the candidate numbers sum to target.
# Each number in candidates may only be used once in the combination.
# 
# Note:
# - The input array may contain duplicate numbers.
# - The resulting combinations must not contain duplicate combinations; each unique combination should appear only once.
#
# Example:
# Input: candidates = [1, 1, 2, 5], target = 3
# Output: [[1, 2]]
# Explanation: Although there are two '1's in the array, the combination [1, 2] should be output only once.
import re


def combination_sum2(candidates, target):
    result  = []
    path =[]
    
    def backtrack(index, remainder):
        if remainder == 0:
            result.append(path.copy())
            return
        
        for i in range(index,len(candidates)):
            value = candidates[i]
            if value>remainder:
                continue
            # this skip the duplicate value
            if i > index and candidates[i] == candidates[i - 1]:
                continue
            path.append(value)
            
            backtrack(i+1, remainder-value)
            
            path.pop()
            
    backtrack(0,target)
    return result

if __name__ == '__main__':
    candidates = [1, 1, 2,4]
    target = 3
    ans = combination_sum2(candidates, target)
    print(ans)