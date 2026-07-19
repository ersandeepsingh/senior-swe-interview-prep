# Minimum Cost For Tickets
#
# LeetCode: 983
# Difficulty: Medium
# Pattern: Weighted scheduling DP
#
# Problem:
# You have planned some train traveling one year in advance. The days of the year that you
# will travel are given as an integer array days. Each day is an integer from 1 to 365.
#
# Train tickets are sold in three different ways:
# - a 1-day pass is sold for costs[0] dollars,
# - a 7-day pass is sold for costs[1] dollars, and
# - a 30-day pass is sold for costs[2] dollars.
#
# Return the minimum number of dollars you need to travel every day in the given list of days.
#
# Example 1:
# Input: days = [1, 4, 6, 7, 8, 20], costs = [2, 7, 15]
# Output: 11
#
# Example 2:
# Input: days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 30, 31], costs = [2, 7, 15]
# Output: 17
#
# Constraints:
# - 1 <= days.length <= 365
# - 1 <= days[i] <= 365
# - days is sorted in increasing order
# - days contains unique integers
# - costs.length == 3
# - 1 <= costs[i] <= 1000

def mincost_tickets(days, costs):
    pass


if __name__ == '__main__':
    days = [1, 4, 6, 7, 8, 20]
    costs = [2, 7, 15]
    ans = mincost_tickets(days, costs)
    print(ans)
