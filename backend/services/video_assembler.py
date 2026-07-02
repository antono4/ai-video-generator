"""
Video Assembler Service
Uses MoviePy to assemble images with text overlays into a video
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Set FFmpeg path for moviepy
import imageio_ffmpeg
os.environ['IMAGEIO_FFMPEG_BINARY'] = imageio_ffmpeg.get_ffmpeg_exe()

from moviepy.editor import ImageClip, concatenate_videoclips

load_dotenv()

class VideoAssembler:
    """Assemble video from images and script"""
    
    def __init__(self):
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.frames_dir = self.output_dir / "frames"
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        
        # Video settings for 9:16 vertical format (Shorts/Reels)
        self.width = 1080
        self.height = 1920
        self.fps = 24
        
        # Load fonts
        self.fonts = self._load_fonts()
    
    def _load_fonts(self):
        """Load fonts with fallback"""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
        
        fonts = {}
        # Try to load custom fonts
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    fonts['title'] = ImageFont.truetype(font_path, 72)
                    fonts['text'] = ImageFont.truetype(font_path, 48)
                    fonts['small'] = ImageFont.truetype(font_path, 32)
                    break
                except:
                    continue
        
        # Fallback to default
        if not fonts:
            fonts['title'] = ImageFont.load_default()
            fonts['text'] = ImageFont.load_default()
            fonts['small'] = ImageFont.load_default()
        
        return fonts
    
    def _get_text_size(self, draw, text, font):
        """Get text bounding box safely"""
        try:
            if hasattr(font, 'getbbox'):
                bbox = font.getbbox(text)
                return bbox[2] - bbox[0], bbox[3] - bbox[1]
            elif hasattr(font, 'getsize'):
                return font.getsize(text)
        except:
            pass
        # Fallback
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
        
    async def assemble_video(self, job_id: str, script: Dict, image_paths: List[str]) -> str:
        """
        Assemble a video from images and script.
        
        Args:
            job_id: Job identifier
            script: Script data with scenes and narration
            image_paths: List of image file paths
        
        Returns:
            Path to the generated video file
        """
        output_video = self.output_dir / f"{job_id}.mp4"
        
        # Create frames with text overlays for each scene
        scene_clips = []
        
        scenes = script.get("scenes", [])
        
        for i, scene in enumerate(scenes):
            scene_duration = scene.get("duration", 5.0)
            narration = scene.get("narration", "")
            image_path = image_paths[i] if i < len(image_paths) else None
            
            # Create frame image with text overlay
            frame_path = await self._create_scene_frame(
                scene_number=scene.get("scene_number", i + 1),
                narration=narration,
                image_path=image_path,
                scene_data=scene,
                job_id=job_id
            )
            
            # Create video clip from image
            clip = ImageClip(frame_path).set_duration(scene_duration)
            scene_clips.append(clip)
        
        # Concatenate all clips
        if scene_clips:
            final_video = concatenate_videoclips(scene_clips, method="compose")
            
            # Write to file
            final_video.write_videofile(
                str(output_video),
                fps=self.fps,
                codec='libx264',
                audio=False,
                preset='medium',
                verbose=False,
                logger=None
            )
        
        return str(output_video)
    
    async def _create_scene_frame(
        self, 
        scene_number: int, 
        narration: str, 
        image_path: Optional[str],
        scene_data: Dict,
        job_id: str
    ) -> str:
        """Create a single scene frame with text overlay"""
        
        # Start with background image or create gradient
        if image_path and Path(image_path).exists():
            try:
                bg_img = Image.open(image_path).convert("RGB")
                # Resize to fit 9:16 format (crop to center)
                target_ratio = self.width / self.height
                img_ratio = bg_img.width / bg_img.height
                
                if img_ratio > target_ratio:
                    # Image is wider - crop sides
                    new_width = int(bg_img.height * target_ratio)
                    left = (bg_img.width - new_width) // 2
                    bg_img = bg_img.crop((left, 0, left + new_width, bg_img.height))
                else:
                    # Image is taller - crop top/bottom
                    new_height = int(bg_img.width / target_ratio)
                    top = (bg_img.height - new_height) // 2
                    bg_img = bg_img.crop((0, top, bg_img.width, top + new_height))
                
                bg_img = bg_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"Error loading image: {e}")
                bg_img = self._create_gradient_frame(scene_number)
        else:
            bg_img = self._create_gradient_frame(scene_number)
        
        # Convert to RGBA for overlay
        bg_img = bg_img.convert("RGBA")
        
        # Add dark overlay for text readability
        overlay = Image.new('RGBA', bg_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Gradient overlay at bottom for text
        gradient_height = self.height // 3
        for y in range(gradient_height):
            alpha = int(180 * (1 - y / gradient_height))
            draw.rectangle([(0, self.height - gradient_height + y), (self.width, self.height - gradient_height + y + 1)],
                          fill=(0, 0, 0, alpha))
        
        # Composite the overlay
        bg_img = Image.alpha_composite(bg_img, overlay)
        bg_img = bg_img.convert("RGB")
        
        # Draw text
        draw = ImageDraw.Draw(bg_img)
        
        # Add scene number badge
        badge_padding = 20
        badge_text = f"Scene {scene_number}"
        badge_w, badge_h = self._get_text_size(draw, badge_text, self.fonts['small'])
        badge_width = badge_w + badge_padding * 2
        badge_height = badge_h + badge_padding * 2
        
        # Draw badge background
        badge_x = self.width - badge_width - 40
        badge_y = 40
        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + badge_width, badge_y + badge_height],
            radius=15,
            fill=(100, 120, 200, 100)
        )
        draw.text((badge_x + badge_padding, badge_y + badge_padding - 5), 
                  badge_text, font=self.fonts['small'], fill=(255, 255, 255))
        
        # Add title/subtitle at top
        title_text = scene_data.get("description", "")[:60]
        if title_text:
            title_w, title_h = self._get_text_size(draw, title_text, self.fonts['title'])
            title_x = (self.width - title_w) // 2
            title_y = 100
            # Draw shadow
            draw.text((title_x + 3, title_y + 3), title_text, font=self.fonts['title'], fill=(0, 0, 0))
            draw.text((title_x, title_y), title_text, font=self.fonts['title'], fill=(255, 255, 255))
        
        # Add narration text at bottom
        if narration:
            # Word wrap the narration
            max_chars_per_line = 35
            words = narration.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line) + len(word) + 1 <= max_chars_per_line:
                    current_line += (" " if current_line else "") + word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            # Draw each line
            line_height = 60
            start_y = self.height - gradient_height - 100 - (len(lines) - 1) * line_height
            
            for j, line in enumerate(lines):
                text_w, text_h = self._get_text_size(draw, line, self.fonts['text'])
                text_x = (self.width - text_w) // 2
                text_y = start_y + j * line_height
                # Draw shadow for readability
                draw.text((text_x + 2, text_y + 2), line, font=self.fonts['text'], fill=(0, 0, 0))
                draw.text((text_x, text_y), line, font=self.fonts['text'], fill=(255, 255, 255))
        
        # Save frame
        frame_path = self.frames_dir / f"{job_id}_frame_{scene_number}.png"
        bg_img.save(frame_path, "PNG", quality=95)
        
        return str(frame_path)
    
    def _create_gradient_frame(self, scene_number: int) -> Image.Image:
        """Create a gradient background frame"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        colors = [
            ((20, 30, 60), (60, 20, 80)),      # Blue to purple
            ((30, 20, 50), (60, 40, 20)),      # Purple to orange
            ((20, 50, 40), (30, 30, 60)),      # Teal to blue
            ((50, 30, 20), (20, 30, 50)),      # Orange to blue
            ((30, 40, 50), (50, 30, 50)),      # Steel to magenta
        ]
        
        base_color, secondary_color = colors[(scene_number - 1) % len(colors)]
        
        for y in range(self.height):
            ratio = y / self.height
            r = int(base_color[0] * (1 - ratio * 0.5) + secondary_color[0] * ratio * 0.5)
            g = int(base_color[1] * (1 - ratio * 0.5) + secondary_color[1] * ratio * 0.5)
            b = int(base_color[2] * (1 - ratio * 0.5) + secondary_color[2] * ratio * 0.5)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        return img
