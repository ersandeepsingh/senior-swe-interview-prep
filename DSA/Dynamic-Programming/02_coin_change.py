# Coin Change
#
# LeetCode: 322
# Difficulty: Medium
# Pattern: Unbounded knapsack
#
# Problem:
# You are given an integer array coins representing coins of different denominations and an
# integer amount representing a total amount of money.
#
# Return the fewest number of coins that you need to make up that amount. If that amount of
# money cannot be made up by any combination of the coins, return -1.
#
# You may assume that you have an infinite number of each kind of coin.
#
# Example 1:
# Input: coins = [1, 2, 5], amount = 11
# Output: 3
# Explanation: 11 = 5 + 5 + 1
#
# Example 2:
# Input: coins = [2], amount = 3
# Output: -1
#
# Example 3:
# Input: coins = [1], amount = 0
# Output: 0
#
# Constraints:
# - 1 <= coins.length <= 12
# - 1 <= coins[i] <= 2^31 - 1
# - 0 <= amount <= 10^4

# Simple naive recursive solution to try all coin combinations.
def coin_change_naive_recursive(coins, amount):
    if amount == 0:
        return 0
    res = float('inf')
    for c in coins:
        if c <= amount:
            sub_res = coin_change_naive_recursive(coins, amount - c)
            if sub_res != -1:
                res = min(res, sub_res + 1)
    return res if res != float('inf') else -1

#  Optimised DP
def coin_change(coins, amount):
    INF = math.inf
    dp = [INF]*(amount+1)
    dp[0] = 0
    for i in range(1, amount+1):
        for c in coins:
            if i>=c:
                dp[i] = min(dp[i], dp[i-c]+1)
        
    return dp[amount]
                

if __name__ == '__main__':
    coins = [1, 2, 5]
    amount = 11
    ans = coin_change(coins, amount)
    print(ans)
