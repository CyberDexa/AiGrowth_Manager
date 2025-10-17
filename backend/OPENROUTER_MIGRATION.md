# OpenRouter API Migration

## Overview
We've successfully migrated all AI services to use OpenRouter's unified API, consolidating from multiple API keys to a single `OPENROUTER_API_KEY`.

## Services Using OpenRouter

### 1. Content Generation (Text)
- **Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **Model**: `anthropic/claude-3.5-sonnet`
- **Purpose**: Generate social media posts, captions, hashtags
- **Status**: ✅ Already implemented and working

### 2. Image Generation
- **Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **Model**: `google/gemini-2.5-flash-image` (Gemini 2.5 Flash "Nano Banana")
- **Method**: Uses `modalities: ["image", "text"]` parameter
- **Purpose**: Generate AI images from text prompts
- **Status**: ✅ Newly migrated (replaces direct OpenAI API)
- **Response Format**: Returns base64 data URL in `choices[0].message.images[0].image_url.url`
- **Pricing**: Extremely cost-effective at ~$0.03 per 1000 images (vs DALL-E 3 at $0.04-$0.12 per image)

## Key Differences from Previous Implementation

### Image Generation Changes
1. **API Endpoint**: Changed from `/images/generations` to `/chat/completions`
2. **Model**: Changed from `openai/dall-e-3` to `google/gemini-2.5-flash-image`
3. **Request Format**: 
   - Old: `{"model": "dall-e-3", "prompt": "...", "size": "...", "quality": "..."}`
   - New: `{"model": "google/gemini-2.5-flash-image", "messages": [{"role": "user", "content": "..."}], "modalities": ["image", "text"]}`
4. **Response Format**:
   - Old: `response.data[0].url`
   - New: `response.choices[0].message.images[0].image_url.url` (base64 data URL)
5. **Image URL**: Returns base64 data URL instead of temporary URL
6. **Prompt Enhancement**: Quality and style preferences are now embedded in the prompt text
7. **Cost**: Dramatically reduced - from $0.04-$0.12 per image to $0.00003 per image (~1000x cheaper!)

## Configuration

### Required Environment Variables
