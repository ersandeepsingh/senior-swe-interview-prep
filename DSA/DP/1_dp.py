# Fibonacci Series

def fib(n):
    if n<=1:
        return n
    return fib(n-1) + fib(n-2)

#Memoisation
def fibDP(n, arr):
    if n<=1:
        return n
    if arr[n] !=-1:
        return arr[n]
    arr[n] = fibDP(n-1, arr) + fibDP(n-2, arr)
    return  arr[n]


# Tabulation
def fibotab(n):
    dp = [0]*(n+1)
    dp[0] = 0
    dp[1] = 1
    for i in range(2,n+1):
        dp[i] = dp[i-1]+dp[i-2]
    return dp[n]

if __name__=="__main__":
    n=6
    arr = [-1]*(n+1)
    print(f"Fibonacci of Memoisation {n} --> ",fibDP(n,arr))
    print(f"Fibonacci of Tabulation {n} --> ",fibotab(n))
