# You are given an integer array coins representing coins of different
# denominations and an integer amount representing a total amount of money.

# Return the fewest number of coins that you need to make up that amount. 
# If that amount of money cannot be made up by any combination of the coins, return -1.

# You may assume that you have an infinite number of each kind of coin.
# Example 1:

# Input: coins = [1,2,5], amount = 11
# Output: 3
# Explanation: 11 = 5 + 5 + 1
# Example 2:

# Input: coins = [2], amount = 3
# Output: -1
# Example 3:

# Input: coins = [1], amount = 0
# Output: 0

def minCoin(coins, amount):
    # Greedy (largest coin first) is wrong for arbitrary coin sets, so we use
    # bottom-up DP. dp[a] = fewest coins needed to make amount `a`.
    # Use amount + 1 as "infinity": it's larger than any real answer
    # (at most `amount` coins of value 1), so it safely marks "unreachable".
    INF = amount + 1
    dp = [0] + [INF] * amount  # dp[0] = 0 coins; every other amount starts unreachable

    # Build every amount from 1..amount using the best solution for smaller amounts.
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                # Take one coin `c`, then reuse the optimal answer for (a - c).
                dp[a] = min(dp[a], dp[a - c] + 1)

    # If dp[amount] was never improved, the amount can't be formed.
    return dp[amount] if dp[amount] != INF else -1

    
if __name__ == "__main__":
    coins = [186,419,83,408]
    amount = 6249
    print(f"min coins for {amount}: ", minCoin(coins, amount))