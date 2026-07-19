# Alien Dictionary
#
# LeetCode: 269
# Difficulty: Hard
# Pattern: Lexicographic from constraints
#
# Problem:
# There is a new alien language that uses the English alphabet. However, the order among
# the letters is unknown to you.
#
# You are given a list of strings words from the alien language's dictionary, where the
# strings in words are sorted lexicographically by the rules of this new language.
#
# Return a string of the unique letters in the new alien language sorted in lexicographically
# increasing order by the new language's rules. If there is no unique order, return any valid
# order. If the given input is invalid, return an empty string.
#
# Example 1:
# Input: words = ["wrt", "wrf", "er", "ett", "rftt"]
# Output: "wertf"
#
# Example 2:
# Input: words = ["z", "x"]
# Output: "zx"
#
# Example 3:
# Input: words = ["z", "x", "z"]
# Output: ""
#
# Constraints:
# - 1 <= words.length <= 100
# - 1 <= words[i].length <= 100
# - words[i] consists of only lowercase English letters

def alien_order(words):
    pass


if __name__ == '__main__':
    words = ["wrt", "wrf", "er", "ett", "rftt"]
    ans = alien_order(words)
    print(ans)
