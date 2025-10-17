"""Mock LinkedIn API responses for testing."""

from datetime import datetime


# Successful responses
LINKEDIN_SHARE_STATISTICS_SUCCESS = {
    "elements": [{
        "totalShareStatistics": {
            "likeCount": 150,
            "commentCount": 25,
            "shareCount": 12,
            "impressionCount": 5500,
            "clickCount": 80,
            "uniqueImpressionsCount": 4800,
            "engagement": 187
        },
        "organizationalEntity": "urn:li:organization:123456",
        "share": "urn:li:share:987654321"
    }]
}

LINKEDIN_POST_DETAILS_SUCCESS = {
    "id": "urn:li:share:987654321",
    "author": "urn:li:organization:123456",
    "created": {
        "time": 1696156800000
    },
    "text": {
        "text": "Test LinkedIn post content"
    },
    "videoViews": 0
}

LINKEDIN_ORGANIZATION_FOLLOWER_STATS_SUCCESS = {
    "elements": [
        {
            "organizationalEntity": "urn:li:organization:123456",
            "timeRange": {
                "start": 1696070400000,
                "end": 1696156800000
            },
            "followerGains": {
                "organicFollowerGain": 50,
                "paidFollowerGain": 10
            },
            "followerCounts": {
                "organicFollowerCount": 10500,
                "paidFollowerCount": 500
            }
        }
    ]
}

# Error responses
LINKEDIN_SHARE_NOT_FOUND = {
    "status": 404,
    "message": "Resource urn:li:share:987654321 not found"
}

LINKEDIN_UNAUTHORIZED = {
    "status": 401,
    "message": "Unauthorized"
}

LINKEDIN_RATE_LIMIT_EXCEEDED = {
    "status": 429,
    "message": "Too many requests"
}

# Empty response (no data)
LINKEDIN_EMPTY_RESPONSE = {
    "elements": []
}

# Minimal response (missing optional fields)
LINKEDIN_MINIMAL_RESPONSE = {
    "elements": [{
        "totalShareStatistics": {
            "likeCount": 10,
            "commentCount": 2,
            "shareCount": 1,
            "impressionCount": 500
        }
    }]
}

# High engagement response
LINKEDIN_HIGH_ENGAGEMENT_RESPONSE = {
    "elements": [{
        "totalShareStatistics": {
            "likeCount": 5000,
            "commentCount": 800,
            "shareCount": 300,
            "impressionCount": 250000,
            "clickCount": 15000,
            "uniqueImpressionsCount": 180000,
            "engagement": 6100
        }
    }]
}
