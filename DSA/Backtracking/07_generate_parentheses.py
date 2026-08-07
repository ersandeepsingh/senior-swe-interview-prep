# Generate Parentheses
#
# LeetCode: 22
# Difficulty: Medium
# Pattern: Parentheses generation
#
# Problem:
# Given n pairs of parentheses, write a function to generate all combinations of well-formed
# parentheses.
#
# Example 1:
# Input: n = 3
# Output: ["((()))","(()())","(())()","()(())","()()()"]
#
# Example 2:
# Input: n = 1
# Output: ["()"]
#
# Constraints:
# - 1 <= n <= 8

def generate_parenthesis(n):
    result = []
    path = []
    
    def backtrack(open,close):
        if len(path) == 2*n:
            result.append(path.copy())
            return
        
        # add open and explore
        if open < n:
            path.append("(")
            backtrack(open+1,close)
            path.pop()
        
         # add close and explore
        if close<open:
            path.append(")")
            backtrack(open,close+1)
            path.pop()
        
    
    backtrack(0,0)
    return result


if __name__ == '__main__':
    n = 3
    ans = generate_parenthesis(n)
    print(ans)
