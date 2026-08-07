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
    def is_palindrome(left,right):
        while left<right:
            if s[left] != s[right]:
                return False
            left+=1
            right-=1
        return True
        
    result = []
    path = []
    def backtrack(index) -> None:
        if len("".join(path)) == len(s):
            result.append(path.copy())
            return
        for right in range(index, len(s)):
            if is_palindrome(index,right):
                path.append(s[index:right+1])
                backtrack(right+1)
                path.pop()
    
    backtrack(0)
    return result

# Antoher way to do this
def partition(s):
    def is_palindrome(left,right):
        while left<right:
            if s[left] != s[right]:
                return False
            left+=1
            right-=1
        return True
    result = []
    path = []
    
    def backtrack(start):
        if start == len(s): # here the difference
            result.append(path.copy())
            return
        for end in range(start, len(s)):
            if is_palindrome(start, end):
                # choose
                path.append(s[start:end+1])
                # explore (note backtrack from end+1, not start+1)
                backtrack(end+1)
                # undo
                path.pop()
    backtrack(0)

if __name__ == '__main__':
    s = "aab"
    ans = partition(s)
    print(ans)
