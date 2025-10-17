# Platform Content Limits & Best Practices

## Overview
Each social media platform has specific content restrictions and best practices. This guide helps you create content that meets all platform requirements.

---

## Twitter / X

### Character Limits
- **Maximum**: 280 characters per tweet
- **Threads**: Can create multiple tweets as a thread if content exceeds 280 characters
- **Recommendation**: Keep tweets concise (240-260 chars) to allow room for retweets with comments

### Content Types
- ✅ Text only
- ✅ Text with images (up to 4 images)
- ✅ Text with video (1 video)
- ✅ Text with GIF (1 GIF)
- ✅ Polls

### Media Limits
- **Images**: Max 4 per tweet, up to 5MB each (JPEG, PNG, GIF, WEBP)
- **Videos**: Max 512MB, up to 2:20 minutes
- **GIF**: Max 15MB

### Best Practices
- Use hashtags sparingly (1-2 per tweet)
- @ mentions count toward character limit
- Links are automatically shortened to 23 characters
- Emojis count as 2 characters each (usually)
- First 100 characters are most important for engagement

### Rate Limits (Free Tier)
- **Posts**: 500 tweets per month
- **API Calls**: Standard rate limits apply

---

## LinkedIn

### Character Limits
- **Maximum**: 3,000 characters per post
- **Recommendation**: 1,300-1,600 characters for optimal engagement
- **First 140 characters**: Appear in feed preview (most important)

### Content Types
- ✅ Text only
- ✅ Text with single image
- ✅ Text with video
- ✅ Text with document (PDF, PPT, DOC)
- ✅ Articles (LinkedIn Publishing)
- ✅ Polls

### Media Limits
- **Images**: 1 image per post, up to 10MB (PNG, JPG)
- **Videos**: Max 10GB, 3 seconds to 10 minutes
- **Documents**: Max 100MB (PDF, PPT, DOC, DOCX)

### Best Practices
- Use line breaks for readability
- 3-5 hashtags optimal
- Post during business hours (Tue-Thu, 9am-12pm)
- Include CTAs (Call To Actions)
- Professional tone

### Visibility Options
- **PUBLIC**: Visible to all LinkedIn members
- **CONNECTIONS**: Only visible to your connections

---

## Facebook

### Character Limits
- **Maximum**: 63,206 characters per post
- **Recommendation**: 40-80 characters for optimal engagement
- **Link posts**: Keep text to 2-3 sentences

### Content Types
- ✅ Text only
- ✅ Text with image(s)
- ✅ Text with video
- ✅ Text with link preview
- ✅ Photo album (up to 10 images)
- ✅ Live video
- ✅ Stories (24-hour ephemeral)

### Media Limits
- **Images**: Max 10 per post, up to 4MB each (JPG, PNG, GIF, BMP)
- **Videos**: Max 1GB, up to 240 minutes
- **Link preview**: Automatically generated from URL

### Best Practices
- Use compelling first sentence (appears in feed)
- Ask questions to drive engagement
- Use Facebook native video (better reach than YouTube links)
- Post 1-2 times per day
- Best times: 1pm-3pm on weekdays

### Page Posting
- Posts appear on Facebook Page
- Can schedule posts
- Supports Page insights and analytics
- Multiple admins can manage

---

## Instagram

### Character Limits
- **Caption**: 2,200 characters maximum
- **Recommendation**: First 125 characters appear without "more" button
- **Hashtags**: 30 maximum per post

### Content Types
- ✅ Photo (single or carousel)
- ✅ Video (Reels, Feed, Stories)
- ✅ Carousel (up to 10 images/videos)
- ✅ Stories (24-hour ephemeral)
- ✅ Reels (short-form video)

### Media Requirements
- **Image required**: Cannot post text-only to Instagram
- **Aspect ratios**: 
  - Square: 1:1 (1080x1080px)
  - Landscape: 1.91:1 (1080x566px)
  - Portrait: 4:5 (1080x1350px)
- **File size**: Max 8MB for images
- **Video**: 3-60 seconds for feed, max 100MB

### Best Practices
- High-quality, visually appealing images required
- Use relevant hashtags (9-12 optimal)
- First line of caption is most important
- Post consistently (1 post per day)
- Best times: 11am-1pm weekdays

### Instagram Business Requirements
- Must have Instagram Business or Creator account
- Must be linked to a Facebook Page
- Cannot post to personal Instagram accounts via API

---

## Platform Comparison

| Platform | Max Characters | Image Required | Best Length | Posting Frequency |
|----------|---------------|----------------|-------------|-------------------|
| Twitter | 280 | No | 240-260 | 3-5/day |
| LinkedIn | 3,000 | No | 1,300-1,600 | 1/day |
| Facebook | 63,206 | No | 40-80 | 1-2/day |
| Instagram | 2,200 | **Yes** | First 125 chars | 1/day |

---

## AI Growth Manager Validation

### Backend Validation
The backend automatically validates content before publishing:

**Twitter:**
```python
if len(content) > 280:
    raise HTTPException(
        status_code=400,
        detail="Twitter posts cannot exceed 280 characters"
    )
```

**LinkedIn:**
- Enforces 3,000 character limit
- Validates visibility parameter

**Meta (Facebook/Instagram):**
- Validates image_url required for Instagram posts
- Checks page_id or instagram_account_id present

### Frontend Warnings
The frontend provides real-time character counting:
- Twitter: Shows "X/280 characters" with warning when approaching limit
- LinkedIn: Shows "X/3,000 characters"
- Instagram: Shows "X/2,200 characters" and requires image upload

---

## Content Optimization Tips

### For Multi-Platform Posting

**Option 1: Platform-Specific Content**
Create separate content for each platform:
- Twitter: Short, punchy, with hashtags
- LinkedIn: Professional, detailed, thought leadership
- Facebook: Conversational, engaging, with media
- Instagram: Visual-first with compelling caption

**Option 2: Adaptive Content**
Start with the most restrictive (Twitter 280 chars):
1. Write core message in 280 characters
2. Expand for LinkedIn (add context, details)
3. Add visual elements for Instagram
4. Adapt tone for Facebook

**Option 3: Thread for Twitter**
If content exceeds 280 characters:
1. Break into multiple tweets (thread)
2. Use AI Growth Manager's thread support
3. Each tweet max 280 characters
4. Numbered format (1/5, 2/5, etc.)

### Character Count Considerations

**What Counts as Characters:**
- Letters, numbers, punctuation: 1 character each
- Spaces: 1 character
- Emojis: Usually 2 characters (some are 4)
- URLs: Shortened by Twitter (23 chars), full length on other platforms
- @ mentions: Full length

**Line Breaks:**
- Twitter: Count as characters
- LinkedIn: Recommended for readability, count as characters
- Facebook: Minimal impact, count as characters

---

## Testing Your Content

### Before Publishing

1. **Check character count**: Use AI Growth Manager's built-in counter
2. **Preview on each platform**: See how it will appear
3. **Test with sample audience**: Use platform's draft/schedule features
4. **Review media**: Ensure images/videos meet requirements

### After Publishing

1. **Monitor first hour**: Quick engagement insights
2. **Adjust strategy**: Based on performance
3. **Cross-post timing**: Stagger multi-platform posts if needed

---

## Error Messages

### Common Validation Errors

**Twitter:**
```
"Twitter posts cannot exceed 280 characters. Your post is 305 characters."
```
**Solution**: Shorten content or use thread feature

**Instagram:**
```
"Instagram posts require an image_url parameter"
```
**Solution**: Upload image before posting to Instagram

**LinkedIn:**
```
"Invalid visibility parameter. Must be 'PUBLIC' or 'CONNECTIONS'"
```
**Solution**: Set visibility parameter correctly

---

## Rate Limits

### Twitter (Free Tier)
- **Monthly**: 500 tweets
- **Daily**: ~16 tweets
- **Per hour**: Recommended 3-5 posts

### LinkedIn
- **Per day**: 25 posts (API limit)
- **Recommended**: 1-2 posts per day

### Facebook
- **Per hour**: 200 API calls
- **No strict post limit**
- **Recommended**: 1-2 posts per day

### Instagram
- **Per day**: 25 posts per account
- **Per hour**: 200 API calls
- **Recommended**: 1 post per day

---

## Future Enhancements

### Planned Features
- ✨ Auto-thread creation for long Twitter content
- ✨ AI-powered content adaptation per platform
- ✨ Character count with emoji detection
- ✨ Link preview optimization
- ✨ Multi-image carousel support
- ✨ Video upload and processing

---

**Last Updated**: 2025-10-17  
**Version**: 1.0

For questions or issues, check the backend validation logic in:
- `backend/app/api/publishing_v2.py`
- `backend/app/services/publishing/`
