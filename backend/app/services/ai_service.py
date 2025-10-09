"""
AI Service for generating marketing strategies using OpenRouter API
"""
from typing import Dict, Any, Optional
import httpx
import json
from app.core.config import settings


class AIService:
    """Service for AI-powered content generation"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "anthropic/claude-3.5-sonnet"  # High-quality model for strategy generation
        
    async def generate_strategy(
        self,
        business_name: str,
        business_description: str,
        target_audience: str,
        marketing_goals: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive marketing strategy using AI
        
        Args:
            business_name: Name of the business
            business_description: Description of the business
            target_audience: Target audience description
            marketing_goals: Marketing goals and objectives
            additional_context: Optional additional context
            
        Returns:
            Dict containing the generated strategy
        """
        
        # Build the prompt
        prompt = self._build_strategy_prompt(
            business_name=business_name,
            business_description=business_description,
            target_audience=target_audience,
            marketing_goals=marketing_goals,
            additional_context=additional_context
        )
        
        # Call OpenRouter API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-growth-manager.com",
            "X-Title": "AI Growth Manager"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert marketing strategist specializing in growth marketing, digital strategy, and content marketing. Generate comprehensive, actionable marketing strategies."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 3000
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
                strategy_text = result["choices"][0]["message"]["content"]
                
                # Parse the strategy into structured format
                parsed_strategy = self._parse_strategy_response(strategy_text)
                
                return {
                    "success": True,
                    "strategy": parsed_strategy,
                    "raw_response": strategy_text,
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
                "error": f"Strategy generation failed: {str(e)}"
            }
    
    def _build_strategy_prompt(
        self,
        business_name: str,
        business_description: str,
        target_audience: str,
        marketing_goals: str,
        additional_context: Optional[str] = None
    ) -> str:
        """Build the AI prompt for strategy generation"""
        
        prompt = f"""Generate a comprehensive marketing strategy for the following business:

**Business Name:** {business_name}

**Business Description:** {business_description}

**Target Audience:** {target_audience}

**Marketing Goals:** {marketing_goals}
"""
        
        if additional_context:
            prompt += f"\n**Additional Context:** {additional_context}\n"
        
        prompt += """

Please provide a detailed marketing strategy with the following sections:

1. **Executive Summary** - Brief overview of the strategy (2-3 sentences)

2. **Market Analysis** - Key insights about the target market and competition

3. **Strategic Objectives** - 3-5 SMART goals aligned with the marketing goals

4. **Channel Strategy** - Recommended marketing channels and why they're suitable:
   - Social Media platforms
   - Content Marketing approaches
   - Email Marketing tactics
   - Paid Advertising opportunities
   - Other relevant channels

5. **Content Pillars** - 4-6 core content themes to focus on

6. **Key Tactics** - Specific actionable tactics for the first 90 days (at least 8-10 tactics)

7. **Success Metrics** - KPIs to track progress (at least 5 metrics)

8. **Budget Considerations** - High-level budget recommendations

9. **Timeline** - Suggested implementation timeline (30/60/90 day milestones)

Format the response in clear sections with markdown formatting. Be specific, actionable, and tailored to this exact business.
"""
        
        return prompt
    
    def _parse_strategy_response(self, strategy_text: str) -> Dict[str, Any]:
        """Parse the AI response into structured format"""
        
        # For now, return the raw text
        # In production, you might parse this into structured JSON
        return {
            "executive_summary": self._extract_section(strategy_text, "Executive Summary"),
            "market_analysis": self._extract_section(strategy_text, "Market Analysis"),
            "objectives": self._extract_section(strategy_text, "Strategic Objectives"),
            "channel_strategy": self._extract_section(strategy_text, "Channel Strategy"),
            "content_pillars": self._extract_section(strategy_text, "Content Pillars"),
            "tactics": self._extract_section(strategy_text, "Key Tactics"),
            "metrics": self._extract_section(strategy_text, "Success Metrics"),
            "budget": self._extract_section(strategy_text, "Budget Considerations"),
            "timeline": self._extract_section(strategy_text, "Timeline"),
            "full_text": strategy_text
        }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from the markdown response"""
        
        import re
        
        # Try to find the section with various markdown header formats
        patterns = [
            rf"\*\*{section_name}\*\*[:\s]*(.+?)(?=\n\*\*|\Z)",
            rf"#{1,3}\s*{section_name}[:\s]*(.+?)(?=\n#{1,3}|\Z)",
            rf"{section_name}[:\s]*(.+?)(?=\n\n[A-Z]|\Z)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""


# Singleton instance
ai_service = AIService()
