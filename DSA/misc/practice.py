def sequentialDigits( low, high):
    digits = "123456789"
    ans = []

    min_len = len(str(low))
    max_len = len(str(high))
    for length in range(min_len, max_len + 1):
        for start in range(10 - length):
            num = int(digits[start:start + length])
            if low <= num <= high:
                ans.append(num)
    return ans

if __name__ == "__main__":
    low = 103
    high =30000000
    print(sequentialDigits(low, high))