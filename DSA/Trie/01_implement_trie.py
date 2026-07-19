# Implement Trie (Prefix Tree)
#
# LeetCode: 208
# Difficulty: Medium
# Pattern: Basic trie
#
# Problem:
# A trie (pronounced as "try") or prefix tree is a tree data structure used to efficiently
# store and retrieve keys in a dataset of strings. There are various applications of this
# data structure, such as autocomplete and spellchecker.
#
# Implement the Trie class:
# - Trie() Initializes the trie object.
# - void insert(String word) Inserts the string word into the trie.
# - boolean search(String word) Returns True if the string word is in the trie (i.e., was
#   inserted before), and False otherwise.
# - boolean startsWith(String prefix) Returns True if there is a previously inserted string
#   word that has the prefix prefix, and False otherwise.
#
# Example 1:
# Input:
# ["Trie", "insert", "search", "search", "startsWith", "insert", "search"]
# [[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]]
# Output: [null, null, true, false, true, null, true]
#
# Constraints:
# - 1 <= word.length, prefix.length <= 2000
# - word and prefix consist only of lowercase English letters
# - At most 3 * 10^4 calls in total will be made to insert, search, and startsWith

class Trie:
    def __init__(self):
        pass

    def insert(self, word):
        pass

    def search(self, word):
        pass

    def starts_with(self, prefix):
        pass


if __name__ == '__main__':
    trie = Trie()
    trie.insert("apple")
    print(trie.search("apple"))
    print(trie.search("app"))
    print(trie.starts_with("app"))
    trie.insert("app")
    print(trie.search("app"))
