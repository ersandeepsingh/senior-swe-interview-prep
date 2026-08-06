# Palindrome Partitioning
#
# LeetCode: 131
# Difficulty: Medium
# Pattern: Partition
#
# Problem:
# Given a string s, partition s such that every substring of the partition is a palindrome.
# Return all possible palindrome partitioning of s.
#
# Example 1:
# Input: s = "aab"
# Output: [["a", "a", "b"], ["aa", "b"]]
#
# Example 2:
# Input: s = "a"
# Output: [["a"]]
#
# Constraints:
# - 1 <= s.length <= 16
# - s contains only lowercase English letters


def partition(s):
    
    def palindrome(left,right):
        while left<right:
            if s[left] != s[right]:
                return False
            left+=1
            right-=1
        return True

    result = []
    path = []
    
    def backtrack(start):
        if start == len(s):
            result.append(path.copy())
            return
        for end in range(start, len(s)):
            if palindrome(start, end):
                # choose
                path.append(s[start:end+1])
                # explore (note backtrack from end+1, not start+1)
                backtrack(end+1)
                # undo
                path.pop()
    backtrack(0)
    return result

if __name__ == '__main__':
    s = "aab"
    ans = partition(s)
    print(ans)
