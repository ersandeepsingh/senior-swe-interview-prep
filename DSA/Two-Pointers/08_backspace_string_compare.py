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

def backspace_compare(s, t):
    # using O(1) space and backspace logic for both strings.
    def get_next_valid_index(string, idx):
        back = 0
        while idx >= 0:
            if string[idx] == "#":
                back += 1
            elif back > 0:
                back -= 1
            else:
                break
            idx -= 1
        return idx

    first = len(s) - 1
    sec = len(t) - 1
    while first >= 0 or sec >= 0:
        first = get_next_valid_index(s, first)
        sec = get_next_valid_index(t, sec)

        if first >= 0 and sec >= 0:
            if s[first] != t[sec]:
                return False
        elif first >= 0 or sec >= 0:
            return False  # One string still has chars, the other doesn't

        first -= 1
        sec -= 1
    return True

if __name__ == '__main__':
    s = "ab#c"
    t = "ad#c"
    ans = backspace_compare(s, t)
    print(ans)
