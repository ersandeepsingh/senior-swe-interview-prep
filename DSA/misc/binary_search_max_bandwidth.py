# Problem: Maximize Final Throughput
#
# You manage n servers. Server i has a base throughput `throughput[i]`.
# You can scale a server by running extra units of it: running a server as
# `k` units delivers `k * throughput[i]` throughput. Going from k units to
# k+1 units (one "scale up") costs `scalingCost[i]`, so reaching `k` units
# costs `(k - 1) * scalingCost[i]`.
#
# The system's final throughput is limited by its weakest server, i.e. it is
# the minimum throughput across all servers. You are given a total `budget`
# that caps the sum of scaling costs across all servers.
#
# Return the maximum final throughput T such that EVERY server can be scaled
# to deliver at least T, without the total scaling cost exceeding `budget`.
#
# Example:
#   throughput = [2, 3], scalingCost = [1, 1], budget = 3
#   To reach T = 6: server 0 needs 3 units (cost 2), server 1 needs 2 units
#   (cost 1), total 3 <= budget -> achievable. T = 6 is the max here.
#
# --- Solution: Binary Search on the Answer ---
#
# Key insight: the predicate "can every server reach at least T within budget?"
# is MONOTONIC. If T is achievable, any smaller T is also achievable (it costs
# no more); if T is not achievable, no larger T is either. This monotonic
# true...true,false...false shape lets us binary search for the largest T that
# is still achievable, instead of trying every value.
#
# can_achieve(target): for each server, the units needed to hit `target` is
# ceil(target / throughput[i]); the number of paid scale-ups is (units - 1),
# costing (units - 1) * scalingCost[i]. Sum across servers and compare to
# budget (short-circuiting as soon as we blow the budget).
#
# Search range: the answer is at least min(throughput) (achievable with zero
# cost) and can't exceed max(throughput) + budget * max(throughput), a safe
# upper bound. We keep the last achievable `mid` as the answer.
#
# Complexity: O(n * log(range)) time, O(1) extra space, where `range` is the
# size of the search interval for T.

import math

def maxFinalThroughput(throughput, scalingCost, budget):
    n = len(throughput)

    # Feasibility check: can every server be scaled to at least `target`
    # without the total scaling cost exceeding `budget`?
    def can_achieve(target):
        total_cost = 0

        for i in range(n):
            # Units of server i needed to reach `target` throughput.
            # ceil because a partial unit still counts as a full one.
            required_units = math.ceil(target / throughput[i])
            # The first unit is free; only the extra units are paid scale-ups.
            scale_times = required_units - 1

            # Add this server's scaling cost to the running total.
            total_cost += scale_times * scalingCost[i]

            # Early exit: once we've blown the budget, `target` is impossible.
            if total_cost > budget:
                return False

        return total_cost <= budget

    # Search bounds for the answer T:
    #   low  = min(throughput): always reachable at zero cost (every server
    #          already delivers at least its own base throughput).
    #   high = a safe over-estimate we know we can never exceed.
    low = min(throughput)
    high = max(throughput) + budget * max(throughput)
    answer = low  # best achievable T found so far

    # Binary search for the largest T where can_achieve(T) is still True.
    while low <= high:
        mid = (low + high) // 2

        if can_achieve(mid):
            # `mid` works, record it and try to push for something larger.
            answer = mid
            low = mid + 1
        else:
            # `mid` is too high, shrink the upper half.
            high = mid - 1

    return answer