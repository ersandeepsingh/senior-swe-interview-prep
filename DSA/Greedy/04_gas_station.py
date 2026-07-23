# Gas Station
#
# LeetCode: 134
# Difficulty: Medium
# Pattern: Gas station circuit
#
# Problem:
# There are n gas stations along a circular route, where the amount of gas at the i-th station
# is gas[i].
#
# You have a car with an unlimited gas tank and it costs cost[i] of gas to travel from the
# i-th station to its next (i + 1)-th station. You begin the journey with an empty tank at
# one of the gas stations.
#
# Given two integer arrays gas and cost, return the starting gas station's index if you can
# travel around the circuit once in the clockwise direction, otherwise return -1. If there
# exists a solution, it is guaranteed to be unique.
#
# Example 1:
# Input: gas = [1, 2, 3, 4, 5], cost = [3, 4, 5, 1, 2]
# Output: 3
#
# Example 2:
# Input: gas = [2, 3, 4], cost = [3, 4, 3]
# Output: -1
#
# Constraints:
# - n == gas.length == cost.length
# - 1 <= n <= 10^5
# - 0 <= gas[i], cost[i] <= 10^4
# - The input is generated such that the answer is unique

# Brute force
def can_complete_circuit(gas, cost):
    """
    Brute force approach: Check each station as a possible starting point.
    """
    n = len(gas)
    for start in range(n):
        tank = 0
        valid = True
        for i in range(n):
            idx = (start + i) % n
            tank += gas[idx] - cost[idx]
            if tank < 0:
                valid = False
                break
        if valid:
            return start
    return -1

# Optimised Grredy Approach
def can_complete_circuit(gas, cost):
    """
    Returns the starting gas station's index if you can travel around the circuit once,
    otherwise returns -1. The input is guaranteed such that the answer is unique if it exists.
    """
    if sum(gas) < sum(cost):
        return -1  # Not enough gas to complete the circuit

    # total: tracks the overall gas surplus/deficit (already checked before, but shown for completeness)
    # curr: tracks the current running sum since last reset (potential starting point)
    # start: starting index candidate for completing the circuit
    curr, start = 0, 0, 0
    for i in range(len(gas)):
        diff = gas[i] - cost[i]  # Net gas after leaving station i
        curr += diff             # Add to the current segment's net gas
        if curr < 0:
            # If we run out of gas before reaching the next station, this can't be a starting point
            start = i + 1       # Next station is the new candidate start
            curr = 0            # Reset current net gas
    return start


if __name__ == '__main__':
    # gas = [1, 2, 3, 4, 5]
    # cost = [3, 4, 5, 1, 2]
    gas = [2, 3, 4]
    cost = [3, 4, 3]
    ans = can_complete_circuit(gas, cost)
    print(ans)
