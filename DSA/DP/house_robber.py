# House Robber
# You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed, the only constraint stopping you from robbing each of them is that adjacent houses have security systems connected and it will automatically contact the police if two adjacent houses were broken into on the same night.

# Given an integer array nums representing the amount of money of each house, return the maximum amount of money you can rob tonight without alerting the police.

 
# Example 1:

# Input: nums = [1,2,3,1]
# Output: 4
# Explanation: Rob house 1 (money = 1) and then rob house 3 (money = 3).
# Total amount you can rob = 1 + 3 = 4.
# Example 2:

# Input: nums = [2,7,9,3,1]
# Output: 12
# Explanation: Rob house 1 (money = 2), rob house 3 (money = 9) and rob house 5 (money = 1).
# Total amount you can rob = 2 + 9 + 1 = 12.
 


def rob(nums):
    n = len(nums)
    if n==0:
        return 0
    if n==1:
        return nums[0]
    dp = [0]*(n)
    dp[0] = nums[0]
    dp[1] = max(nums[0],nums[1])
    for i in range(2, n):
        dp[i] = max(dp[i-2]+nums[i], dp[i-1])
    return dp[n-1]
            
# if the house is not circle
def robcircle(nums):
    n = len(nums)
    dp = [0]*(n)
    if n==0:
        return 0
    if n==1:
        return nums[0]
    dp[0] = nums[0]
    dp[1] = max(nums[0],nums[1])
    # In the circular case, the first and last houses are adjacent.
    # So, we cannot rob both the first and the last house.
    # Thus, take the maximum of (rob houses [0...n-2]) and (rob houses [1...n-1])
    def rob_linear(lst):
        m = len(lst)
        if m==0:
            return 0
        if m==1:
            return lst[0]
        dp = [0]*m
        dp[0] = lst[0]
        dp[1] = max(lst[0], lst[1])
        for i in range(2, m):
            dp[i] = max(dp[i-2]+lst[i], dp[i-1])
        return dp[-1]
    if n == 2:
        return max(nums[0], nums[1])
    return max(rob_linear(nums[1:]), rob_linear(nums[:-1]))


## optimised approach
def robcircle(nums):
    n = len(nums)
    if n == 0:
        return 0
    if n == 1:
        return nums[0]

    def rob_linear(lst):
        prev = curr = 0
        for x in lst:
            prev, curr = curr, max(curr, prev + x)
        return curr

    # Houses 0 and n-1 are adjacent, so exclude one end or the other.
    return max(rob_linear(nums[1:]), rob_linear(nums[:-1]))

if __name__=="__main__":
    cost = [1,100,1,1,1,100,1,1,100,1]
    costcircle = [1,6,3,1,8]
    print(f"max rob --> ",rob(cost))
    print(f"max rob --> ",robcircle(costcircle))


