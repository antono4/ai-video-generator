"""
Image Generator Service
Generates scene images using AI APIs or creates placeholder images
"""

import os
import uuid
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv

load_dotenv()

class ImageGenerator:
    """Generate images for video scenes"""
    
    def __init__(self):
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        self.openai_key = os.getenv("OPENAI_IMAGE_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.leonardo_key = os.getenv("LEONARDO_API_KEY")
        self.use_mock = not (self.openai_key or self.leonardo_key)
    
    async def generate_image(self, prompt: str, scene_number: int, job_id: str) -> str:
        """
        Generate an image for a scene.
        
        Args:
            prompt: Image generation prompt
            scene_number: Scene number for naming
            job_id: Job ID for organizing files
        
        Returns:
            Path to the generated image
        """
        if self.use_mock:
            return self._create_placeholder_image(prompt, scene_number, job_id)
        
        # Try OpenAI DALL-E first, then Leonardo AI
        if self.openai_key:
            return await self._generate_with_dalle(prompt, scene_number, job_id)
        elif self.leonardo_key:
            return await self._generate_with_leonardo(prompt, scene_number, job_id)
        
        return self._create_placeholder_image(prompt, scene_number, job_id)
    
    async def _generate_with_dalle(self, prompt: str, scene_number: int, job_id: str) -> str:
        """Generate image using DALL-E API"""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.openai_key)
            
            # Enhance prompt for better results
            enhanced_prompt = f"{prompt}, professional quality, 4K, high detail, cinematic lighting, dramatic composition"
            
            response = await client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1792x1024",  # 16:9 aspect ratio
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Download the image
            import requests
            image_response = requests.get(image_url)
            
            filename = f"{job_id}_scene_{scene_number}.png"
            filepath = self.images_dir / filename
            filepath.write_bytes(image_response.content)
            
            return str(filepath)
            
        except Exception as e:
            print(f"DALL-E API error: {e}, using placeholder")
            return self._create_placeholder_image(prompt, scene_number, job_id)
    
    async def _generate_with_leonardo(self, prompt: str, scene_number: int, job_id: str) -> str:
        """Generate image using Leonardo AI API"""
        try:
            import requests
            
            enhanced_prompt = f"{prompt}, cinematic, 4K, high detail, professional photography"
            
            headers = {
                "Authorization": f"Bearer {self.leonardo_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": enhanced_prompt,
                "model_id": "6bef9f1b-29f4-4d3b-a8c4-3a5c9d7e8f1a",  # Leonardo Vision model
                "width": 1024,
                "height": 1024,
                "steps": 30,
                "guidance_scale": 7.5
            }
            
            # Create generation request
            response = requests.post(
                "https://cloud.leonardo.ai/api/rest/v1/generations",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Leonardo API error: {response.text}")
            
            generation_id = response.json().get("sdGenerationJob", {}).get("generationId")
            
            # Poll for completion (simplified - in production, use webhooks)
            import asyncio
            for _ in range(30):  # Max 30 seconds wait
                await asyncio.sleep(1)
                status_response = requests.get(
                    f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                    headers=headers
                )
                status = status_response.json()
                if status.get("generations_by_id", [{}])[0].get("status") == "COMPLETE":
                    image_url = status["generations_by_id"][0]["image_url"]
                    break
            
            # Download the image
            image_response = requests.get(image_url)
            
            filename = f"{job_id}_scene_{scene_number}.png"
            filepath = self.images_dir / filename
            filepath.write_bytes(image_response.content)
            
            return str(filepath)
            
        except Exception as e:
            print(f"Leonardo AI error: {e}, using placeholder")
            return self._create_placeholder_image(prompt, scene_number, job_id)
    
    def _create_placeholder_image(self, prompt: str, scene_number: int, job_id: str) -> str:
        """Create a stylized placeholder image"""
        # Create a 1920x1080 image (16:9)
        width, height = 1920, 1080
        
        # Create gradient background
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Create animated gradient based on scene number
        colors = [
            (20, 30, 50),    # Deep blue
            (30, 20, 50),    # Deep purple
            (20, 50, 40),    # Deep teal
            (50, 30, 20),    # Deep orange
            (30, 40, 50),    # Steel blue
        ]
        
        base_color = colors[(scene_number - 1) % len(colors)]
        
        # Draw gradient
        for y in range(height):
            ratio = y / height
            r = int(base_color[0] * (1 - ratio * 0.3))
            g = int(base_color[1] * (1 - ratio * 0.3))
            b = int(base_color[2] * (1 - ratio * 0.3))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add decorative elements
        import random
        random.seed(scene_number * 1000)
        
        # Draw abstract shapes
        for _ in range(5):
            x1 = random.randint(0, width - 100)
            y1 = random.randint(0, height - 100)
            size = random.randint(50, 200)
            x2 = x1 + size
            y2 = y1 + size
            shape_color = (
                random.randint(100, 200),
                random.randint(100, 200),
                random.randint(150, 255)
            )
            draw.ellipse([x1, y1, x2, y2], fill=shape_color, outline=None)
        
        # Add glassmorphism panel
        panel_width, panel_height = 800, 400
        panel_x = (width - panel_width) // 2
        panel_y = (height - panel_height) // 2
        
        # Draw blurred background effect (approximate)
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Semi-transparent panel
        for i in range(20):
            alpha = 80 + i * 3
            offset = 20 - i
            overlay_draw.rounded_rectangle(
                [panel_x - offset, panel_y - offset, 
                 panel_x + panel_width + offset, panel_y + panel_height + offset],
                radius=30,
                fill=(255, 255, 255, min(alpha, 150))
            )
        
        img.paste(overlay, (0, 0), overlay)
        
        # Add scene number
        draw = ImageDraw.Draw(img)
        try:
            # Try to use a nice font
            font_size = 120
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw scene number with glow effect
        scene_text = f"SCENE {scene_number}"
        text_bbox = draw.textbbox((0, 0), scene_text, font=small_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (width - text_width) // 2
        text_y = panel_y + 60
        
        # Glow effect
        for offset_y in range(-3, 4):
            for offset_x in range(-3, 4):
                draw.text((text_x + offset_x, text_y + offset_y), scene_text, 
                         font=small_font, fill=(100, 150, 255, 100))
        
        draw.text((text_x, text_y), scene_text, font=small_font, fill=(200, 220, 255))
        
        # Draw main prompt text (truncated)
        display_text = prompt[:50] + "..." if len(prompt) > 50 else prompt
        prompt_bbox = draw.textbbox((0, 0), display_text, font=font)
        prompt_width = prompt_bbox[2] - prompt_bbox[0]
        prompt_x = (width - prompt_width) // 2
        prompt_y = panel_y + 150
        
        draw.text((prompt_x, prompt_y), display_text, font=font, fill=(255, 255, 255))
        
        # Add AI generated indicator
        indicator_text = "✨ AI Generated Scene"
        indicator_bbox = draw.textbbox((0, 0), indicator_text, font=small_font)
        indicator_width = indicator_bbox[2] - indicator_bbox[0]
        indicator_x = (width - indicator_width) // 2
        indicator_y = panel_y + panel_height - 80
        
        draw.text((indicator_x, indicator_y), indicator_text, font=small_font, fill=(180, 200, 255))
        
        # Save image
        filename = f"{job_id}_scene_{scene_number}.png"
        filepath = self.images_dir / filename
        img.save(filepath, "PNG", quality=95)
        
        return str(filepath)
