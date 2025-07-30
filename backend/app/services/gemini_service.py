"""
Gemini AI service for generating cultural intelligence explanations.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
import aiohttp
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for generating AI explanations using Google Gemini API."""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        
    async def generate_recommendation_explanation(
        self, 
        user_profile: Dict[str, Any], 
        recommendation: Dict[str, Any],
        context: str = "music_discovery"
    ) -> str:
        """Generate AI explanation for a cultural recommendation."""
        
        if not self.api_key:
            raise Exception("Gemini API key is required but not configured. Please set GOOGLE_GEMINI_API_KEY environment variable.")
        
        prompt = self._build_explanation_prompt(user_profile, recommendation, context)
        explanation = await self._call_gemini_api(prompt)
        return explanation
    
    async def generate_cultural_insight_explanation(
        self, 
        insight: Dict[str, Any], 
        user_context: Dict[str, Any]
    ) -> str:
        """Generate explanation for cultural insights."""
        
        if not self.api_key:
            raise Exception("Gemini API key is required but not configured. Please set GOOGLE_GEMINI_API_KEY environment variable.")
        
        prompt = self._build_insight_prompt(insight, user_context)
        explanation = await self._call_gemini_api(prompt)
        return explanation
    
    async def generate_trend_prediction_explanation(
        self, 
        prediction: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> str:
        """Generate explanation for trend predictions."""
        
        if not self.api_key:
            raise Exception("Gemini API key is required but not configured. Please set GOOGLE_GEMINI_API_KEY environment variable.")
        
        prompt = self._build_trend_prompt(prediction, user_profile)
        explanation = await self._call_gemini_api(prompt)
        return explanation
    
    def _build_explanation_prompt(
        self, 
        user_profile: Dict[str, Any], 
        recommendation: Dict[str, Any], 
        context: str
    ) -> str:
        """Build prompt for recommendation explanations."""
        
        music_prefs = user_profile.get("music_preferences", [])
        languages = user_profile.get("content_languages", [])
        geographic_interests = user_profile.get("geographic_interests", [])
        
        prompt = f"""
You are a cultural intelligence expert analyzing music recommendations. Provide a clear, engaging explanation for why this recommendation makes sense.

User Profile:
- Music Preferences: {', '.join(music_prefs)}
- Languages: {', '.join(languages)}
- Geographic Interests: {', '.join(geographic_interests)}

Recommendation:
- Category: {recommendation.get('category', 'Unknown')}
- Title: {recommendation.get('title', 'Unknown')}
- Description: {recommendation.get('description', 'Unknown')}
- Cultural Impact: {recommendation.get('cultural_impact', 0)}%

Context: {context}

Generate a concise, personalized explanation (2-3 sentences) that:
1. Connects the recommendation to the user's existing preferences
2. Explains the cultural significance or benefit
3. Makes it sound exciting and actionable

Keep it conversational and inspiring. Focus on cultural discovery and growth.
"""
        return prompt
    
    def _build_insight_prompt(self, insight: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Build prompt for cultural insight explanations."""
        
        prompt = f"""
You are a cultural intelligence analyst explaining a data-driven insight. Make it clear and actionable.

Cultural Insight:
- Category: {insight.get('category', 'Unknown')}
- Finding: {insight.get('finding', 'Unknown')}
- Confidence: {insight.get('confidence', 0)}%

User Context:
- Cultural Score: {user_context.get('cultural_score', 0)}%
- Diversity Index: {user_context.get('diversity_index', 0)}%

Provide a clear explanation (2-3 sentences) that:
1. Explains what this insight means in practical terms
2. Why it's significant for cultural development
3. What action the user could take based on this insight

Be encouraging and specific about the cultural benefits.
"""
        return prompt
    
    def _build_trend_prompt(self, prediction: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Build prompt for trend prediction explanations."""
        
        prompt = f"""
You are a cultural trend analyst explaining why a specific trend is predicted to be relevant for this user.

Trend Prediction:
- Trend: {prediction.get('nextTrend', 'Unknown')}
- Probability: {prediction.get('probability', 0)}%
- Timeframe: {prediction.get('timeframe', 'Unknown')}
- Category: {prediction.get('category', 'Unknown')}

User Profile:
- Music Preferences: {', '.join(user_profile.get('music_preferences', []))}
- Geographic Interests: {', '.join(user_profile.get('geographic_interests', []))}

Explain (2-3 sentences):
1. Why this trend aligns with the user's profile
2. What makes this trend culturally significant
3. How the user can engage with or benefit from this trend

Make it sound like an exciting opportunity for cultural exploration.
"""
        return prompt
    
    async def _call_gemini_api(self, prompt: str) -> str:
        """Make API call to Gemini."""
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 200,
                "stopSequences": []
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
        }
        
        url = f"{self.base_url}?key={self.api_key}"
        
        timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if "candidates" in result and len(result["candidates"]) > 0:
                        content = result["candidates"][0]["content"]["parts"][0]["text"]
                        return content.strip()
                    else:
                        raise Exception("No candidates in response")
                else:
                    error_text = await response.text()
                    raise Exception(f"API call failed: {response.status} - {error_text}")
    

# Global service instance
gemini_service = GeminiService()