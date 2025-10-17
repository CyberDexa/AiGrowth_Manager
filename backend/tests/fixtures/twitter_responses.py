"""Mock Twitter API responses for testing."""

# Successful responses
TWITTER_TWEET_SUCCESS = {
    "data": {
        "id": "1234567890123456789",
        "text": "Test tweet content with #hashtags and @mentions",
        "created_at": "2025-10-01T12:00:00.000Z",
        "public_metrics": {
            "like_count": 200,
            "reply_count": 30,
            "retweet_count": 45,
            "quote_count": 8,
            "bookmark_count": 15,
            "impression_count": 12000
        },
        "non_public_metrics": {
            "impression_count": 12000,
            "url_link_clicks": 150,
            "user_profile_clicks": 25
        },
        "organic_metrics": {
            "impression_count": 11500,
            "like_count": 195,
            "reply_count": 29,
            "retweet_count": 43,
            "url_link_clicks": 145
        }
    }
}

TWITTER_MULTIPLE_TWEETS_SUCCESS = {
    "data": [
        {
            "id": "1111111111111111111",
            "text": "First test tweet",
            "public_metrics": {
                "like_count": 100,
                "reply_count": 10,
                "retweet_count": 20,
                "quote_count": 5,
                "bookmark_count": 8
            }
        },
        {
            "id": "2222222222222222222",
            "text": "Second test tweet",
            "public_metrics": {
                "like_count": 150,
                "reply_count": 15,
                "retweet_count": 30,
                "quote_count": 7,
                "bookmark_count": 12
            }
        }
    ]
}

TWITTER_USER_METRICS_SUCCESS = {
    "data": {
        "id": "9876543210",
        "username": "testuser",
        "name": "Test User",
        "created_at": "2020-01-01T00:00:00.000Z",
        "public_metrics": {
            "followers_count": 5000,
            "following_count": 1200,
            "tweet_count": 3500,
            "listed_count": 45
        }
    }
}

# Error responses
TWITTER_TWEET_NOT_FOUND = {
    "errors": [
        {
            "value": "1234567890123456789",
            "detail": "Could not find tweet with id: 1234567890123456789",
            "title": "Not Found Error",
            "resource_type": "tweet",
            "parameter": "id",
            "type": "https://api.twitter.com/2/problems/resource-not-found"
        }
    ]
}

TWITTER_UNAUTHORIZED = {
    "errors": [
        {
            "message": "Unauthorized",
            "type": "https://api.twitter.com/2/problems/not-authorized-for-resource"
        }
    ],
    "title": "Unauthorized",
    "status": 401
}

TWITTER_RATE_LIMIT_EXCEEDED = {
    "errors": [
        {
            "message": "Rate limit exceeded",
            "type": "https://api.twitter.com/2/problems/usage-capped"
        }
    ],
    "title": "Too Many Requests",
    "status": 429
}

# Minimal response (only public metrics)
TWITTER_MINIMAL_RESPONSE = {
    "data": {
        "id": "1234567890123456789",
        "text": "Minimal tweet",
        "public_metrics": {
            "like_count": 5,
            "reply_count": 1,
            "retweet_count": 2,
            "quote_count": 0,
            "bookmark_count": 1
        }
    }
}

# High engagement response
TWITTER_HIGH_ENGAGEMENT_RESPONSE = {
    "data": {
        "id": "1234567890123456789",
        "text": "Viral tweet content",
        "created_at": "2025-10-01T12:00:00.000Z",
        "public_metrics": {
            "like_count": 50000,
            "reply_count": 2000,
            "retweet_count": 10000,
            "quote_count": 500,
            "bookmark_count": 3000,
            "impression_count": 5000000
        },
        "non_public_metrics": {
            "impression_count": 5000000,
            "url_link_clicks": 50000,
            "user_profile_clicks": 10000
        }
    }
}

# Video tweet response
TWITTER_VIDEO_TWEET_SUCCESS = {
    "data": {
        "id": "1234567890123456789",
        "text": "Check out this video!",
        "attachments": {
            "media_keys": ["3_1234567890"]
        },
        "public_metrics": {
            "like_count": 500,
            "reply_count": 50,
            "retweet_count": 100,
            "quote_count": 20,
            "bookmark_count": 75
        },
        "non_public_metrics": {
            "impression_count": 50000,
            "url_link_clicks": 500,
            "user_profile_clicks": 100
        }
    },
    "includes": {
        "media": [
            {
                "media_key": "3_1234567890",
                "type": "video",
                "duration_ms": 30000,
                "public_metrics": {
                    "view_count": 25000
                }
            }
        ]
    }
}
