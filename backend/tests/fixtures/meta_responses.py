"""Mock Meta (Facebook & Instagram) API responses for testing."""

# Facebook Post Responses
FACEBOOK_POST_SUCCESS = {
    "id": "123456789_987654321",
    "created_time": "2025-10-01T12:00:00+0000",
    "message": "Test Facebook post content",
    "reactions": {
        "summary": {
            "total_count": 300
        }
    },
    "comments": {
        "summary": {
            "total_count": 50
        }
    },
    "shares": {
        "count": 20
    },
    "permalink_url": "https://facebook.com/123456789/posts/987654321"
}

FACEBOOK_INSIGHTS_SUCCESS = {
    "data": [
        {"name": "post_impressions", "values": [{"value": 8000}]},
        {"name": "post_impressions_unique", "values": [{"value": 6500}]},
        {"name": "post_engaged_users", "values": [{"value": 370}]},
        {"name": "post_clicks", "values": [{"value": 120}]},
        {"name": "post_video_views", "values": [{"value": 0}]}
    ]
}

FACEBOOK_PAGE_INSIGHTS_SUCCESS = {
    "data": [
        {"name": "page_impressions", "values": [{"value": 50000}]},
        {"name": "page_impressions_unique", "values": [{"value": 35000}]},
        {"name": "page_post_engagements", "values": [{"value": 2500}]},
        {"name": "page_fans", "values": [{"value": 10500}]},
        {"name": "page_fan_adds", "values": [{"value": 150}]},
        {"name": "page_fan_removes", "values": [{"value": 30}]}
    ]
}

# Instagram Media Responses
INSTAGRAM_MEDIA_SUCCESS = {
    "id": "123456789",
    "media_type": "IMAGE",
    "media_url": "https://scontent.cdninstagram.com/...",
    "permalink": "https://instagram.com/p/ABC123/",
    "timestamp": "2025-10-01T12:00:00+0000",
    "like_count": 450,
    "comments_count": 35,
    "caption": "Test Instagram post #hashtag"
}

INSTAGRAM_INSIGHTS_SUCCESS = {
    "data": [
        {"name": "impressions", "values": [{"value": 9500}]},
        {"name": "reach", "values": [{"value": 8200}]},
        {"name": "engagement", "values": [{"value": 485}]},
        {"name": "saved", "values": [{"value": 25}]},
        {"name": "video_views", "values": [{"value": 0}]}
    ]
}

INSTAGRAM_VIDEO_MEDIA_SUCCESS = {
    "id": "987654321",
    "media_type": "VIDEO",
    "media_url": "https://scontent.cdninstagram.com/...",
    "permalink": "https://instagram.com/p/XYZ789/",
    "timestamp": "2025-10-01T12:00:00+0000",
    "like_count": 800,
    "comments_count": 60,
    "caption": "Check out this video! #viral"
}

INSTAGRAM_VIDEO_INSIGHTS_SUCCESS = {
    "data": [
        {"name": "impressions", "values": [{"value": 25000}]},
        {"name": "reach", "values": [{"value": 20000}]},
        {"name": "engagement", "values": [{"value": 860}]},
        {"name": "saved", "values": [{"value": 50}]},
        {"name": "video_views", "values": [{"value": 15000}]}
    ]
}

# Error responses
FACEBOOK_POST_NOT_FOUND = {
    "error": {
        "message": "(#803) Some of the aliases you requested do not exist: 123456789_987654321",
        "type": "OAuthException",
        "code": 803,
        "fbtrace_id": "ABC123XYZ"
    }
}

FACEBOOK_UNAUTHORIZED = {
    "error": {
        "message": "Invalid OAuth access token.",
        "type": "OAuthException",
        "code": 190,
        "fbtrace_id": "DEF456UVW"
    }
}

FACEBOOK_RATE_LIMIT_EXCEEDED = {
    "error": {
        "message": "Application request limit reached",
        "type": "OAuthException",
        "code": 4,
        "error_subcode": 2446079,
        "fbtrace_id": "GHI789RST"
    }
}

INSTAGRAM_MEDIA_NOT_FOUND = {
    "error": {
        "message": "(#803) Some of the aliases you requested do not exist: 123456789",
        "type": "OAuthException",
        "code": 803,
        "fbtrace_id": "JKL012MNO"
    }
}

# Minimal responses
FACEBOOK_MINIMAL_POST = {
    "id": "123456789_987654321",
    "created_time": "2025-10-01T12:00:00+0000",
    "message": "Simple post",
    "reactions": {
        "summary": {
            "total_count": 10
        }
    },
    "comments": {
        "summary": {
            "total_count": 2
        }
    }
}

INSTAGRAM_MINIMAL_MEDIA = {
    "id": "123456789",
    "media_type": "IMAGE",
    "permalink": "https://instagram.com/p/ABC123/",
    "timestamp": "2025-10-01T12:00:00+0000",
    "like_count": 15,
    "comments_count": 3
}

# High engagement responses
FACEBOOK_HIGH_ENGAGEMENT_POST = {
    "id": "123456789_987654321",
    "created_time": "2025-10-01T12:00:00+0000",
    "message": "Viral Facebook post!",
    "reactions": {
        "summary": {
            "total_count": 50000
        }
    },
    "comments": {
        "summary": {
            "total_count": 5000
        }
    },
    "shares": {
        "count": 2000
    },
    "permalink_url": "https://facebook.com/123456789/posts/987654321"
}

FACEBOOK_HIGH_ENGAGEMENT_INSIGHTS = {
    "data": [
        {"name": "post_impressions", "values": [{"value": 5000000}]},
        {"name": "post_impressions_unique", "values": [{"value": 3500000}]},
        {"name": "post_engaged_users", "values": [{"value": 57000}]},
        {"name": "post_clicks", "values": [{"value": 50000}]},
        {"name": "post_video_views", "values": [{"value": 0}]}
    ]
}

INSTAGRAM_HIGH_ENGAGEMENT_MEDIA = {
    "id": "987654321",
    "media_type": "IMAGE",
    "media_url": "https://scontent.cdninstagram.com/...",
    "permalink": "https://instagram.com/p/VIRAL123/",
    "timestamp": "2025-10-01T12:00:00+0000",
    "like_count": 100000,
    "comments_count": 5000,
    "caption": "This went viral! #viral #trending"
}

INSTAGRAM_HIGH_ENGAGEMENT_INSIGHTS = {
    "data": [
        {"name": "impressions", "values": [{"value": 2000000}]},
        {"name": "reach", "values": [{"value": 1500000}]},
        {"name": "engagement", "values": [{"value": 105000}]},
        {"name": "saved", "values": [{"value": 10000}]},
        {"name": "video_views", "values": [{"value": 0}]}
    ]
}

# Story responses (Instagram)
INSTAGRAM_STORY_MEDIA = {
    "id": "story123456",
    "media_type": "STORY",
    "media_url": "https://scontent.cdninstagram.com/...",
    "timestamp": "2025-10-01T12:00:00+0000"
}

INSTAGRAM_STORY_INSIGHTS = {
    "data": [
        {"name": "impressions", "values": [{"value": 5000}]},
        {"name": "reach", "values": [{"value": 4500}]},
        {"name": "exits", "values": [{"value": 500}]},
        {"name": "replies", "values": [{"value": 50}]}
    ]
}
