# You are given n items whose weights and values are known, 
# as well as a knapsack to carry these items. The knapsack cannot carry more 
# than a certain maximum weight, known as its capacity.

# You need to maximize the total value of the items in your knapsack, 
# while ensuring that the sum of the weights of the selected items does not 
# exceed the capacity of the knapsack.

# If there is no combination of weights whose sum is within the capacity constraint, 
# return 0 


def find_max_knapsack_profit(capacity, weights, values):
    m = len(values)
    # Recursive brute force: at each item we branch into take vs. skip.
    # State = (capacity still available, index of the item we're deciding on).
    def knapsack(remaining_capacity, i):
        # Base case: no items left to consider, or no room left -> zero profit.
        if i < 0 or remaining_capacity <= 0:
            return 0
        # Option 1: skip item i and move to the previous item.
        not_take = knapsack(remaining_capacity, i-1)
        # Option 2: take item i, but only if its weight fits in the remaining capacity.
        take = 0
        if weights[i] <= remaining_capacity:
            take = values[i] + knapsack(remaining_capacity - weights[i], i-1)
        # The best profit at this state is the better of the two choices.
        return max(not_take, take)
    # Kick off from the last item with the full capacity available.
    return knapsack(capacity, m-1)

def dp_knapsack(capacity, weights, values):
    m = len(values)
    # dp[i][c] = best total value achievable using the first i items
    # with a knapsack of capacity c.
    # Row 0 (no items) and column 0 (no capacity) are all zeros, which is
    # why we size the table (m+1) x (capacity+1) and start the loops at 1.
    dp = [[0] * (capacity + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for c in range(capacity + 1):
            # Baseline: skip item i-1, so we inherit the best value from the
            # row above at the same capacity.
            dp[i][c] = dp[i - 1][c]
            # Only consider taking item i-1 if it actually fits in capacity c.
            if weights[i - 1] <= c:
                # Take it: add its value, then use the best value for the
                # remaining capacity (c - weight) from the previous items.
                dp[i][c] = max(dp[i][c], values[i - 1] + dp[i - 1][c - weights[i - 1]])
    # Bottom-right cell = best value using all items at full capacity.
    return dp[m][capacity]


if __name__ == "__main__":
    capacity = 5
    weights = [1, 2, 3]
    values = [10, 15, 40]
    print("recursive:", find_max_knapsack_profit(capacity, weights, values))
    print("dp:", dp_knapsack(capacity, weights, values))
