# 3867. Sum of GCD of Formed Pairs

# You are given an integer array nums of length n.
# Construct an array prefixGcd where for each index i:
# Let mxi = max(nums[0], nums[1], ..., nums[i]).
# prefixGcd[i] = gcd(nums[i], mxi).
# After constructing prefixGcd:

# Sort prefixGcd in non-decreasing order.
# Form pairs by taking the smallest unpaired element and the largest unpaired element.
# Repeat this process until no more pairs can be formed.
# For each formed pair, compute the gcd of the two elements.
# If n is odd, the middle element in the prefixGcd array remains unpaired and should be ignored.
# Return an integer denoting the sum of the GCD values of all formed pairs.

# The term gcd(a, b) denotes the greatest common divisor of a and b.


class Solution:
    def gcdSum(self, nums: list[int]) -> int:
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a

        prefixGcd = []
        max_i = 0
        for x in nums:
            max_i = max(max_i, x)
            prefixGcd.append(gcd(x, max_i))

        prefixGcd.sort()

        # Pair smallest with largest. If n is odd, middle stays unpaired — ignore it.
        # Bug before: `while left <= right` added the middle element when left == right.
        left, right = 0, len(prefixGcd) - 1
        result = 0
        while left < right:
            result += gcd(prefixGcd[left], prefixGcd[right])
            left += 1
            right -= 1
        return result


if __name__ == "__main__":
    sol = Solution()
    # Example 1: prefixGcd = [2,6,2] -> sorted [2,2,6] -> gcd(2,6)=2 (ignore middle) -> 2
    print(sol.gcdSum([2, 6, 4]))
    # Example 2: prefixGcd = [3,6,2,8] -> sorted [2,3,6,8] -> gcd(2,8)+gcd(3,6) = 2+3 = 5
    print(sol.gcdSum([3, 6, 2, 8]))
