"""
Script Generator Service
Uses LLM APIs (OpenAI GPT or Google Gemini) to generate video scripts
"""

import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class ScriptGenerator:
    """Generate video scripts using LLM APIs"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.use_mock = not (self.openai_key or self.google_key)
    
    async def generate(self, prompt: str, duration: int = 30, style: str = "cinematic") -> Dict:
        """
        Generate a video script based on the prompt.
        
        Args:
            prompt: User's topic/prompt for the video
            duration: Target duration in seconds
            style: Visual style (cinematic, animated, realistic)
        
        Returns:
            Dictionary with title, scenes, and total_duration
        """
        if self.use_mock:
            return self._generate_mock_script(prompt, duration, style)
        
        # Try OpenAI first, then Google Gemini
        if self.openai_key:
            return await self._generate_with_openai(prompt, duration, style)
        elif self.google_key:
            return await self._generate_with_gemini(prompt, duration, style)
        
        # Fallback to mock
        return self._generate_mock_script(prompt, duration, style)
    
    async def _generate_with_openai(self, prompt: str, duration: int, style: str) -> Dict:
        """Generate script using OpenAI API"""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.openai_key)
            
            # Calculate number of scenes based on duration (each scene ~5 seconds)
            num_scenes = max(3, duration // 5)
            
            system_prompt = f"""You are a professional video script writer. Create engaging video scripts for {style} style videos.
            Return ONLY valid JSON with this exact structure:
            {{
                "title": "Video Title",
                "scenes": [
                    {{
                        "scene_number": 1,
                        "description": "Scene description",
                        "duration": 5.0,
                        "image_prompt": "Detailed image generation prompt for this scene",
                        "narration": "Voiceover/narration text for this scene"
                    }}
                ],
                "total_duration": {duration}
            }}
            Make the narration engaging and the image prompts detailed for AI image generation."""
            
            user_prompt = f"Create a {duration}-second {style} video script about: {prompt}"
            
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            # Clean and parse JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            script = json.loads(content.strip())
            return script
            
        except Exception as e:
            print(f"OpenAI API error: {e}, falling back to mock")
            return self._generate_mock_script(prompt, duration, style)
    
    async def _generate_with_gemini(self, prompt: str, duration: int, style: str) -> Dict:
        """Generate script using Google Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.google_key)
            model = genai.GenerativeModel('gemini-pro')
            
            num_scenes = max(3, duration // 5)
            
            prompt_text = f"""You are a professional video script writer. Create an engaging {duration}-second {style} video script about: {prompt}
            
            Return ONLY valid JSON with this exact structure:
            {{
                "title": "Video Title",
                "scenes": [
                    {{
                        "scene_number": 1,
                        "description": "Scene description",
                        "duration": 5.0,
                        "image_prompt": "Detailed image generation prompt for this scene",
                        "narration": "Voiceover/narration text for this scene"
                    }}
                ],
                "total_duration": {duration}
            }}
            Create {num_scenes} scenes. Make narration engaging and image prompts detailed."""
            
            response = model.generate_content(prompt_text)
            content = response.text.strip()
            
            # Clean JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            script = json.loads(content.strip())
            return script
            
        except Exception as e:
            print(f"Gemini API error: {e}, falling back to mock")
            return self._generate_mock_script(prompt, duration, style)
    
    def _generate_mock_script(self, prompt: str, duration: int, style: str) -> Dict:
        """Generate a mock script for demo/testing purposes"""
        num_scenes = max(3, duration // 5)
        scene_duration = duration / num_scenes
        
        scenes = []
        topics = [
            f"A breathtaking introduction to {prompt}",
            f"Key concepts and main ideas about {prompt}",
            f"Deep dive into the details of {prompt}",
            f"Examples and applications of {prompt}",
            f"Conclusion and summary of {prompt}"
        ]
        
        for i in range(num_scenes):
            scene_topic = topics[i] if i < len(topics) else f"Scene about {prompt}"
            
            scenes.append({
                "scene_number": i + 1,
                "description": f"{style.title()} visualization of {scene_topic}",
                "duration": scene_duration,
                "image_prompt": f"{style} style, professional quality, dramatic lighting, {scene_topic}, 4K, high detail",
                "narration": f"In this segment, we explore {scene_topic}. This is the voiceover narration that would accompany this visual scene in the final video production."
            })
        
        return {
            "title": f"Understanding {prompt.title()}",
            "scenes": scenes,
            "total_duration": duration
        }
