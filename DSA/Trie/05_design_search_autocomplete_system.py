# Design Search Autocomplete System
#
# LeetCode: 642
# Difficulty: Hard
# Pattern: Autocomplete / search system
#
# Problem:
# Design a search autocomplete system for a search engine. Users may input a sentence (at
# least one word and end with a special character '#').
#
# Implement the AutocompleteSystem class:
# - AutocompleteSystem(String[] sentences, int[] times) Initializes the object with the
#   sentences and times arrays.
# - List<String> input(char c) The next character from the user's input is given. Returns
#   the top 3 historical hot sentences that have the same prefix as the part of the sentence
#   already typed. If there are fewer than 3 matches, return them all. When the user finishes
#   a sentence with '#', auto-complete the system history and return an empty list.
#
# Example 1:
# See LeetCode 642 for the full interactive example with sentences and times.
#
# Constraints:
# - n == sentences.length
# - n == times.length
# - 1 <= n <= 100
# - 1 <= sentences[i].length <= 100
# - 1 <= times[i] <= 50
# - c is a lowercase English letter, a space character, or a hashtag
# - At most 2000 calls will be made to input

class AutocompleteSystem:
    def __init__(self, sentences, times):
        pass

    def input(self, c):
        pass


if __name__ == '__main__':
    sentences = ["i love you", "island", "iroman", "i love leetcode"]
    times = [5, 3, 2, 2]
    ac = AutocompleteSystem(sentences, times)
    print(ac.input("i"))
    print(ac.input(" "))
    print(ac.input("a"))
    print(ac.input("#"))
