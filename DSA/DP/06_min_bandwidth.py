import math
def findMinimumPlansForBandwidth(planSizes, targetBandwidth):
    # Write your code here
    n = len(planSizes)
    m = targetBandwidth
    # The check 'dp[i][b - planSizes[i - 1]] != INF' is not strictly necessary here.
    # Even if dp[i][b - planSizes[i - 1]] is INF, taking min with INF is safe and we do not need to skip the update.
    # The DP update works safely with min().
    INF = math.inf
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = 0  # zero plans needed to make bandwidth 0

    for i in range(1, n + 1):
        for b in range(m + 1):
            # Option 1: don't use the ith plan
            dp[i][b] = dp[i-1][b]
            # Option 2: use the ith plan (can use it multiple times)
            if b >= planSizes[i - 1]:
                dp[i][b] = min(dp[i][b], dp[i][b - planSizes[i - 1]] + 1)

    print(dp)
    return dp[n][m] if dp[n][m] != INF else -1

if __name__ == '__main__':
    planSizes = [1, 2, 5]
    targetBandwidth = 11

    result = findMinimumPlansForBandwidth(planSizes, targetBandwidth)

    print(result)
