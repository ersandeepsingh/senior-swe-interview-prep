# Minimum Cost For Tickets
# You have planned some train traveling one year in advance. The days of the year in which you will travel are given as an integer array days. Each day is an integer from 1 to 365.

# Train tickets are sold in three different ways:

# a 1-day pass is sold for costs[0] dollars,
# a 7-day pass is sold for costs[1] dollars, and
# a 30-day pass is sold for costs[2] dollars.
# The passes allow that many days of consecutive travel.

# For example, if we get a 7-day pass on day 2, then we can travel for 7 days: 2, 3, 4, 5, 6, 7, and 8.
# Return the minimum number of dollars you need to travel every day in the given list of days.

# Input: days = [1,4,6,7,8,20], costs = [2,7,15]
# Output: 11
# Explanation: For example, here is one way to buy passes that lets you travel your travel plan:
# On day 1, you bought a 1-day pass for costs[0] = $2, which covered day 1.
# On day 3, you bought a 7-day pass for costs[1] = $7, which covered days 3, 4, ..., 9.
# On day 20, you bought a 1-day pass for costs[0] = $2, which covered day 20.
# In total, you spent $11 and covered all the days of your travel.
# Constraints:

# 1 <= days.length <= 365
# 1 <= days[i] <= 365
# days is in strictly increasing order.
# costs.length == 3
# 1 <= costs[i] <= 1000

def mincostTickets(days, costs):
    """
    Calendar DP (works because every day is in [1, 365]).

    State:
        dp[d] = minimum cost to cover ALL travel days from day 1 up to day d.

    Key idea:
        We only need to buy a pass on days we actually travel. On every travel
        day d, we buy a pass that ENDS on d and covers a window of calendar
        days backward:
            1-day  pass bought on d -> covers [d,     d]
            7-day  pass bought on d -> covers [d - 6, d]
            30-day pass bought on d -> covers [d - 29, d]

        Any travel days before that window were already paid for, so we add
        the pass price to dp[day_before_window].

    Example (days = [1,4,6,7,8,20], costs = [2,7,15]):
        d=1  -> 1-day pass -> dp[1] = 2
        d=7  -> 7-day pass -> dp[7] = dp[0] + 7 = 7  (window [1,7] hits travel days 1,4,6,7)
        d=8  -> 1-day pass -> dp[8] = dp[7] + 2 = 9  (7-day pass on d=7 ends at 7, so day 8 needs more)
        d=20 -> 1-day pass -> dp[20] = dp[19] + 2 = 11
    """
    # O(1) lookup: is day d a travel day?
    travel_days = set(days)
    # days is sorted, so the last element is the final day we must reach.
    last_day = days[-1]

    # dp[d] stores min cost from day 1 through day d.
    # Size last_day + 1 so we can index directly by calendar day.
    dp = [0] * (last_day + 1)

    for d in range(1, last_day + 1):
        if d not in travel_days:
            # No ticket needed today; cost unchanged since yesterday.
            dp[d] = dp[d - 1]
            continue

        # --- Option 1: buy a 1-day pass ending on d ---
        # Covers only day d, so previous cost is dp[d - 1].
        buy_1 = dp[d - 1] + costs[0]

        # --- Option 2: buy a 7-day pass ending on d ---
        # Covers [d - 6, d]. Last uncovered day is d - 7, so add dp[d - 7].
        # max(0, ...) handles early days (e.g. d = 3 -> look at dp[0] = 0).
        buy_7 = dp[max(0, d - 7)] + costs[1]

        # --- Option 3: buy a 30-day pass ending on d ---
        # Same logic: window is [d - 29, d], cost before it is dp[d - 30].
        buy_30 = dp[max(0, d - 30)] + costs[2]

        dp[d] = min(buy_1, buy_7, buy_30)

    return dp[last_day]
        
if __name__=='__main__':
    days = [1,4,6,7,8,20]
    costs = [2,7,15]
    print(mincostTickets(days, costs))
    