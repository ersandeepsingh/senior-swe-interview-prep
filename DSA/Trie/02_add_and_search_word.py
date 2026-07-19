# Add and Search Word - Data structure design
#
# LeetCode: 211
# Difficulty: Medium
# Pattern: Wildcard search
#
# Problem:
# Design a data structure that supports adding new words and finding if a string matches any
# previously added string.
#
# Implement the WordDictionary class:
# - WordDictionary() Initializes the object.
# - void addWord(word) Adds word to the data structure, it can be matched later.
# - bool search(word) Returns True if there is any string in the data structure that matches
#   word or False otherwise. word may contain dots '.' where dots can be matched with any letter.
#
# Example 1:
# Input:
# ["WordDictionary","addWord","addWord","addWord","search","search","search","search"]
# [[],["bad"],["dad"],["mad"],["pad"],["bad"],[".ad"],["b.."]]
# Output: [null, null, null, null, false, true, true, true]
#
# Constraints:
# - 1 <= word.length <= 25
# - word in addWord consists of lowercase English letters
# - word in search consist of '.' or lowercase English letters
# - There will be at most 2 dots in word for search queries
# - At most 10^4 calls will be made to addWord and search

class WordDictionary:
    def __init__(self):
        pass

    def add_word(self, word):
        pass

    def search(self, word):
        pass


if __name__ == '__main__':
    wd = WordDictionary()
    wd.add_word("bad")
    wd.add_word("dad")
    wd.add_word("mad")
    print(wd.search("pad"))
    print(wd.search("bad"))
    print(wd.search(".ad"))
    print(wd.search("b.."))
