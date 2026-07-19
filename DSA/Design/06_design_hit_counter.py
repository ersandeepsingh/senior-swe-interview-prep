# Design Hit Counter
#
# LeetCode: 362
# Difficulty: Medium
# Pattern: Rate limiter / hit counter
#
# Problem:
# Design a hit counter which counts the number of hits received in the past 5 minutes
# (i.e., the past 300 seconds).
#
# Your system should accept a timestamp parameter (in seconds granularity), and you may
# assume that calls are being made to the system in chronological order (i.e., timestamp is
# monotonically increasing). Several hits may arrive roughly at the same time.
#
# Implement the HitCounter class:
# - HitCounter() Initializes the object of the hit counter system.
# - void hit(int timestamp) Records a hit that happened at timestamp (in seconds).
#   Several hits may happen at the same timestamp.
# - int getHits(int timestamp) Returns the number of hits in the past 5 minutes from
#   timestamp (i.e., the number of hits in the inclusive range [timestamp - 299, timestamp]).
#
# Example 1:
# Input:
# ["HitCounter", "hit", "hit", "hit", "getHits", "hit", "getHits", "getHits"]
# [[], [1], [2], [3], [4], [300], [300], [301]]
# Output: [null, null, null, null, 3, null, 4, 3]
#
# Constraints:
# - 1 <= timestamp <= 2 * 10^9
# - All the calls are being made to the system in chronological order (i.e., timestamp is monotonically increasing)
# - At most 300 calls will be made to hit and getHits

class HitCounter:
    def __init__(self):
        pass

    def hit(self, timestamp):
        pass

    def get_hits(self, timestamp):
        pass


if __name__ == '__main__':
    hc = HitCounter()
    hc.hit(1)
    hc.hit(2)
    hc.hit(3)
    print(hc.get_hits(4))
    hc.hit(300)
    print(hc.get_hits(300))
    print(hc.get_hits(301))
