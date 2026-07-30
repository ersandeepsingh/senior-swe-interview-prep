# Valid Palindrome
#
# LeetCode: 125
# Difficulty: Easy
# Pattern: Palindrome checks
#
# Problem:
# A phrase is a palindrome if, after converting all uppercase letters into
# lowercase letters and removing all non-alphanumeric characters, it reads the
# same forward and backward.
#
# Alphanumeric characters include letters and numbers.
#
# Given a string s, return True if it is a palindrome, or False otherwise.
#
# Example 1:
# Input: s = "A man, a plan, a canal: Panama"
# Output: True
# Explanation:
# After cleaning, the string becomes "amanaplanacanalpanama", which is a
# palindrome.
#
# Example 2:
# Input: s = "race a car"
# Output: False
# Explanation:
# After cleaning, the string becomes "raceacar", which is not a palindrome.
#
# Example 3:
# Input: s = " "
# Output: True
# Explanation:
# After removing non-alphanumeric characters, s becomes an empty string.
# An empty string is considered a palindrome.
#
# Constraints:
# - 1 <= s.length <= 2 * 10^5
# - s consists only of printable ASCII characters

def is_palindrome(s):
    left = 0
    right = len(s)-1
    while left<=right:
        if not s[left].isalnum():
            left+=1
            continue
        if not s[right].isalnum():
            right-=1
            continue
        elif s[left].lower() != s[right].lower():
            return False
        left+=1
        right-=1
    return True

if __name__ == '__main__':
    s = "A man, a plan, a canal: Panama"
    ans = is_palindrome(s)
    print(ans)
