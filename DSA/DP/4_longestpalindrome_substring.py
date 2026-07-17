# Given a string s, return the longest palindromic substring in s.

# Example 1:

# Input: s = "babad"
# Output: "bab"
# Explanation: "aba" is also a valid answer.
# Example 2:

# Input: s = "cbbd"
# Output: "bb"

def isPalindrome(str, left, right):
    if left >= right:
        return True
    if str[left] !=str[right]:
        return False
    return isPalindrome(str, left+1, right-1)

def largestPalindromicSubstring(str):
    # Brute force approach:
    # For every possible substring, check if it is a palindrome.
    # Track the longest palindromic substring.
    
    n = len(str)
    max_len = 0
    start_idx = 0
    
    # Outer loop for the start of substring
    for i in range(n):
        # Inner loop for the end of substring
        for j in range(i, n):
            # Check if the substring from i to j is a palindrome
            if isPalindrome(str, i, j):
                curr_len = j - i + 1
                # Update the result if this palindrome is longest so far
                if curr_len > max_len:
                    max_len = curr_len
                    start_idx = i
                    
    # Return the longest palindromic substring found
    return str[start_idx:start_idx + max_len]

    # Explanation:
    # 1. We check all substrings (i, j) for whether they're palindromes.
    # 2. We compare the length of palindrome found with the max_len tracked so far.
    # 3. If found longer, record its start index and length.
    # 4. Finally, return the substring using slice operation.




if __name__ == "__main__":
    str = "abccba"
    left = 0 
    right = len(str)-1
    print(isPalindrome(str, left, right))