"""
Content Generation Service for creating social media posts using AI
"""
from typing import Dict, Any, Optional, List
import httpx
import json
from app.core.config import settings


class ContentGenerationService:
    """Service for AI-powered content generation"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "anthropic/claude-3.5-sonnet"
        
    async def generate_content(
        self,
        business_name: str,
        business_description: str,
        target_audience: str,
        platform: str,
        content_type: str = "post",
        tone: str = "professional",
        topic: Optional[str] = None,
        additional_context: Optional[str] = None,
        num_posts: int = 1
    ) -> Dict[str, Any]:
        """
        Generate social media content using AI
        
        Args:
            business_name: Name of the business
            business_description: Description of the business
            target_audience: Target audience description
            platform: Social media platform (linkedin, twitter, etc.)
            content_type: Type of content (post, thread, article)
            tone: Tone of the content (professional, casual, etc.)
            topic: Specific topic for the content
            additional_context: Any additional context
            num_posts: Number of posts to generate
            
        Returns:
            Dict containing generated content
        """
        
        # Debug logging
        print(f"DEBUG: API key type: {type(self.api_key)}, value: {repr(self.api_key)}")
        
        # Build the prompt
        prompt = self._build_content_prompt(
            business_name=business_name,
            business_description=business_description,
            target_audience=target_audience,
            platform=platform,
            content_type=content_type,
            tone=tone,
            topic=topic,
            additional_context=additional_context,
            num_posts=num_posts
        )
        
        # Call OpenRouter API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-growth-manager.com",
            "X-Title": "AI Growth Manager"
        }
        
        print(f"DEBUG: Headers: {headers}")
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert social media content creator. Generate engaging, platform-optimized content that drives engagement and achieves business goals."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8,
            "max_tokens": 2000
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Extract the generated content
                content_text = result["choices"][0]["message"]["content"]
                
                # Parse the content into structured format
                parsed_content = self._parse_content_response(
                    content_text, 
                    platform, 
                    num_posts
                )
                
                # Validate and enforce character limits (especially Twitter)
                if platform.lower() == "twitter":
                    for post in parsed_content:
                        full_text = f"{post['text']} {post['hashtags']}".strip()
                        if len(full_text) > 280:
                            # Truncate to 277 characters and add "..."
                            max_length = 277
                            truncated = full_text[:max_length] + "..."
                            # Split back into text and hashtags
                            post['text'] = truncated
                            post['hashtags'] = ""
                            post['_truncated'] = True
                
                return {
                    "success": True,
                    "content": parsed_content,
                    "raw_response": content_text,
                    "model_used": self.model,
                    "tokens_used": result.get("usage", {})
                }
                
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"API request failed: {e.response.status_code}",
                "details": e.response.text
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Content generation failed: {str(e)}"
            }
    
    def _build_content_prompt(
        self,
        business_name: str,
        business_description: str,
        target_audience: str,
        platform: str,
        content_type: str,
        tone: str,
        topic: Optional[str],
        additional_context: Optional[str],
        num_posts: int
    ) -> str:
        """Build the AI prompt for content generation"""
        
        # Platform-specific guidelines
        platform_guidelines = {
            "linkedin": {
                "max_length": 3000,
                "style": "Professional, thought leadership, industry insights",
                "hashtags": "3-5 relevant hashtags",
                "best_practices": "Start with a hook, use line breaks, include a call-to-action"
            },
            "twitter": {
                "max_length": 280,
                "style": "Concise, engaging, conversational",
                "hashtags": "1-2 SHORT hashtags maximum (keep total under 260 chars to leave room)",
                "best_practices": "Hook in first 100 characters, every character counts including spaces and hashtags"
            },
            "facebook": {
                "max_length": 2000,
                "style": "Friendly, community-focused, engaging",
                "hashtags": "2-3 hashtags",
                "best_practices": "Ask questions, encourage comments, use emojis sparingly"
            },
            "instagram": {
                "max_length": 2200,
                "style": "Visual-first, authentic, inspiring",
                "hashtags": "10-15 hashtags",
                "best_practices": "Tell a story, use emojis, include call-to-action"
            }
        }
        
        guidelines = platform_guidelines.get(platform.lower(), platform_guidelines["linkedin"])
        
        # Special Twitter length warning
        twitter_warning = ""
        if platform.lower() == "twitter":
            twitter_warning = f"\n\n⚠️ **CRITICAL TWITTER REQUIREMENT:**\nThe ENTIRE post (text + hashtags + spaces + emojis) MUST be ≤280 characters.\nCount EVERY character. If you use hashtags, keep them SHORT.\nExample: 'Great tips for small business growth! 🚀 #SmallBiz #Growth' = 68 chars\nAim for 250-260 characters max to be safe."
        
        prompt = f"""Generate {num_posts} engaging social media {"post" if num_posts == 1 else "posts"} for the following business:

**Business:** {business_name}
**Description:** {business_description}
**Target Audience:** {target_audience}
**Platform:** {platform.upper()}
**Content Type:** {content_type}
**Tone:** {tone}
"""
        
        if topic:
            prompt += f"**Topic:** {topic}\n"
        
        if additional_context:
            prompt += f"**Additional Context:** {additional_context}\n"
        
        prompt += f"""

**Platform Guidelines:**
- Maximum length: {guidelines['max_length']} characters
- Style: {guidelines['style']}
- Hashtags: {guidelines['hashtags']}
- Best practices: {guidelines['best_practices']}{twitter_warning}

**Content Requirements:**
1. Create compelling, {tone} content that resonates with {target_audience}
2. Include a strong hook in the first line
3. Provide value (educate, inspire, or entertain)
4. {f"Use MAX 1-2 SHORT hashtags (like #AI #Growth, not #LongHashtagsLikeThis)" if platform.lower() == "twitter" else "Include relevant hashtags at the end"}
5. Add a clear call-to-action
6. Keep it authentic and aligned with the business goals
{"7. FOR TWITTER: Total length including ALL text, spaces, emojis, and hashtags MUST be ≤280 chars" if platform.lower() == "twitter" else ""}

**IMPORTANT OUTPUT FORMAT:**
Provide ONLY the final post text with hashtags included.
Do NOT include:
- Character counts like "(269 characters):"
- Labels like "POST TEXT:" or "HASHTAGS:"
- Metadata like "(comma-separated):"
- Explanations or commentary

Just output the ready-to-publish post text.
"""
        
        return prompt
    
    def _parse_content_response(
        self, 
        content_text: str, 
        platform: str,
        num_posts: int
    ) -> List[Dict[str, str]]:
        """Parse the AI response into structured content"""
        import re
        
        posts = []
        
        # Clean up the response - remove common metadata patterns
        cleaned_text = content_text.strip()
        
        # Remove character count markers like "(269 characters):"
        cleaned_text = re.sub(r'\(\d+\s+characters?\)[:：]?\s*', '', cleaned_text, flags=re.IGNORECASE)
        
        # Remove metadata labels like "POST TEXT:", "HASHTAGS:", etc.
        cleaned_text = re.sub(r'^(POST TEXT|HASHTAGS|EXPLANATION|COMMA-SEPARATED)[:：]?\s*', '', cleaned_text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove section headers
        cleaned_text = re.sub(r'\*\*POST TEXT\*\*[:：]?\s*', '', cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r'\*\*HASHTAGS\*\*[:：]?\s*', '', cleaned_text, flags=re.IGNORECASE)
        
        # Remove quotation marks at start/end if present
        cleaned_text = cleaned_text.strip('"').strip("'")
        
        if num_posts == 1:
            # Single post - use cleaned text directly
            # Extract hashtags if they're on separate lines
            lines = cleaned_text.split('\n')
            post_lines = []
            hashtags = []
            
            for line in lines:
                line = line.strip()
                # Check if line is just hashtags (starts with # or is comma-separated hashtags)
                if line.startswith('#') or (line and all(word.startswith('#') or word == ',' for word in line.split())):
                    hashtags.append(line)
                elif line:
                    post_lines.append(line)
            
            post_text = '\n'.join(post_lines).strip()
            hashtag_text = ' '.join(hashtags).strip()
            
            posts.append({
                "text": post_text,
                "hashtags": hashtag_text,
                "platform": platform
            })
        else:
            # Multiple posts - try to split by post markers
            post_pattern = r"(?:Post|POST)\s*(\d+)[:\s]*(.*?)(?=(?:Post|POST)\s*\d+|$)"
            matches = re.findall(post_pattern, cleaned_text, re.DOTALL | re.IGNORECASE)
            
            if matches:
                for _, post_content in matches:
                    post_content = post_content.strip()
                    posts.append({
                        "text": post_content,
                        "hashtags": "",
                        "platform": platform
                    })
            else:
                # Fallback: treat as single post
                posts.append({
                    "text": cleaned_text,
                    "hashtags": "",
                    "platform": platform
                })
        
        return posts
    
    def _extract_section(self, text: str, start_marker: str, end_marker: Optional[str]) -> str:
        """Extract a section from the text between markers"""
        
        import re
        
        if end_marker:
            pattern = rf"{start_marker}[:\s]*(.*?)(?={end_marker})"
        else:
            pattern = rf"{start_marker}[:\s]*(.*)"
        
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return ""


# Singleton instance
content_service = ContentGenerationService()
