# Design Twitter
#
# LeetCode: 355
# Difficulty: Medium
# Pattern: Tweet timeline
#
# Problem:
# Design a simplified version of Twitter where users can post tweets, follow/unfollow another
# user, and is able to see the 10 most recent tweets in the user's news feed.
#
# Implement the Twitter class:
# - Twitter() Initializes your twitter object.
# - void postTweet(int userId, int tweetId) Composes a new tweet with ID tweetId by the user
#   userId. Each call to this function will be made with a unique tweetId.
# - List<Integer> getNewsFeed(int userId) Retrieves the 10 most recent tweet IDs in the user's
#   news feed. Each item in the news feed must be posted by users who the user followed or by
#   the user themself. Tweets must be ordered from most recent to least recent.
# - void follow(int followerId, int followeeId) The user with ID followerId started following
#   the user with ID followeeId.
# - void unfollow(int followerId, int followeeId) The user with ID followerId started
#   unfollowing the user with ID followeeId.
#
# Example 1:
# Input:
# ["Twitter", "postTweet", "getNewsFeed", "follow", "postTweet", "getNewsFeed", "unfollow", "getNewsFeed"]
# [[], [1, 5], [1], [1, 2], [2, 6], [1], [1, 2], [1]]
# Output: [null, null, [5], null, null, [6, 5], null, [5]]
#
# Constraints:
# - 1 <= userId, followerId, followeeId <= 500
# - 0 <= tweetId <= 10^4
# - All the tweets have unique IDs
# - At most 3 * 10^4 calls will be made to postTweet, getNewsFeed, follow, and unfollow

class Twitter:
    def __init__(self):
        pass

    def post_tweet(self, user_id, tweet_id):
        pass

    def get_news_feed(self, user_id):
        pass

    def follow(self, follower_id, followee_id):
        pass

    def unfollow(self, follower_id, followee_id):
        pass


if __name__ == '__main__':
    tw = Twitter()
    tw.post_tweet(1, 5)
    print(tw.get_news_feed(1))
    tw.follow(1, 2)
    tw.post_tweet(2, 6)
    print(tw.get_news_feed(1))
    tw.unfollow(1, 2)
    print(tw.get_news_feed(1))
