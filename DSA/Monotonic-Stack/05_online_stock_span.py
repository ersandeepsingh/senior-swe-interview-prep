# Online Stock Span
#
# LeetCode: 901
# Difficulty: Medium
# Pattern: Span / stock
#
# Problem:
# Design an algorithm that collects daily price quotes for some stock and returns the span
# of that stock's price for the current day.
#
# The span of the stock's price in one day is the maximum number of consecutive days
# (starting from that day and going backward) for which the stock price was less than or
# equal to the price of that day.
#
# Implement the StockSpanner class:
# - StockSpanner() Initializes the object of the class.
# - int next(int price) Returns the span of the stock's price given that today's price is price.
#
# Example 1:
# Input:
# ["StockSpanner", "next", "next", "next", "next", "next", "next", "next"]
# [[], [100], [80], [60], [70], [60], [75], [85]]
# Output: [null, 1, 1, 1, 2, 1, 4, 6]
#
# Constraints:
# - 1 <= price <= 10^5
# - At most 10^4 calls will be made to next

class StockSpanner:
    def __init__(self):
        pass

    def next(self, price):
        pass


if __name__ == '__main__':
    ss = StockSpanner()
    for price in [100, 80, 60, 70, 60, 75, 85]:
        print(ss.next(price))
