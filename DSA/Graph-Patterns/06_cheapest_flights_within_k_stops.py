# Cheapest Flights Within K Stops
#
# LeetCode: 787
# Difficulty: Medium
# Pattern: Dijkstra (weighted)
#
# Problem:
# There are n cities connected by some number of flights. You are given an array flights
# where flights[i] = [from_i, to_i, price_i] indicates that there is a flight from city
# from_i to city to_i with cost price_i.
#
# You are also given three integers src, dst, and k. Return the cheapest price from src to
# dst with at most k stops. If there is no such route, return -1.
#
# Example 1:
# Input: n = 4, flights = [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], src = 0, dst = 3, k = 1
# Output: 700
#
# Example 2:
# Input: n = 3, flights = [[0, 1, 100], [1, 2, 100], [0, 2, 500]], src = 0, dst = 2, k = 1
# Output: 200
#
# Constraints:
# - 1 <= n <= 100
# - 0 <= flights.length <= (n * (n - 1) / 2)
# - flights[i].length == 3
# - 0 <= from_i, to_i < n
# - from_i != to_i
# - 1 <= price_i <= 10^4
# - There will not be any multiple flights between two cities
# - 0 <= src, dst, k < n
# - src != dst

def find_cheapest_price(n, flights, src, dst, k):
    pass


if __name__ == '__main__':
    n = 4
    flights = [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]]
    src, dst, k = 0, 3, 1
    ans = find_cheapest_price(n, flights, src, dst, k)
    print(ans)
