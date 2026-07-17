# Backspace String Compare
#
# LeetCode: 844
# Difficulty: Easy
# Pattern: String compare with skips
#
# Problem:
# Given two strings s and t, return True if they are equal when both are typed
# into empty text editors.
#
# The character "#" means a backspace.
#
# If a backspace is applied to an empty text editor, the text remains empty.
#
# Follow-up:
# Can you solve it in O(n) time and O(1) space?
#
# Example 1:
# Input: s = "ab#c", t = "ad#c"
# Output: True
# Explanation:
# Both strings become "ac".
#
# Example 2:
# Input: s = "ab##", t = "c#d#"
# Output: True
# Explanation:
# Both strings become an empty string.
#
# Example 3:
# Input: s = "a#c", t = "b"
# Output: False
# Explanation:
# s becomes "c", while t becomes "b".
#
# Constraints:
# - 1 <= s.length, t.length <= 200
# - s and t only contain lowercase letters and "#" characters
