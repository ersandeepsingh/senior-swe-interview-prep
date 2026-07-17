# Fibonacci Series

def numberOfWays(n):
    if n==1 or n==2:
        return n
    return numberOfWays(n-1) + numberOfWays(n-2)

#Memoisation
def numberOfWaysDP(n, arr):
    if n==2 or n==1:
        return n
    if arr[n] != -1:
        return arr[n]
    arr[n] = numberOfWaysDP(n-1, arr) + numberOfWaysDP(n-2, arr)
    return  arr[n]


# Tabulation
def numberOfWaysTab(n):
    dp = [0]*(n+1)
    dp[1] = 1
    dp[2] = 2
    for i in range(3,n+1):
        dp[i] = dp[i-1]+dp[i-2]
    return dp[n]

# Tabulation more optimised with O(1) space
def numberOfWaysTab(n):
    if n==1 or n==2:
        return n
    prev1 = 1
    prev2 = 2
    result = 0
    for i in range(3,n+1):
        result = prev1+prev2
        prev1=prev2
        prev2=result
    return result

if __name__=="__main__":
    n=4
    arr = [-1]*(n+1)
    print(f"numberOfWays of Recusrion {n} --> ",numberOfWays(n))
    print(f"numberOfWays of Memoisation {n} --> ",numberOfWaysDP(n,arr))
    print(f"numberOfWays of Tabulation {n} --> ",numberOfWaysTab(20))
