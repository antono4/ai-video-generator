"""
Video generation routes
Handles script generation, image generation, and video assembly
"""

import os
import uuid
import asyncio
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.script_generator import ScriptGenerator
from services.image_generator import ImageGenerator
from services.video_assembler import VideoAssembler
from routes.status import update_job_status

router = APIRouter()

class VideoRequest(BaseModel):
    prompt: str
    duration: Optional[int] = 30  # Total video duration in seconds
    style: Optional[str] = "cinematic"  # cinematic, animated, realistic

class ScriptScene(BaseModel):
    scene_number: int
    description: str
    duration: float  # Duration in seconds
    image_prompt: str
    narration: str

class ScriptResponse(BaseModel):
    job_id: str
    title: str
    scenes: List[ScriptScene]
    total_duration: float

class VideoResponse(BaseModel):
    job_id: str
    status: str
    video_url: Optional[str] = None
    download_url: Optional[str] = None

@router.post("/generate-script", response_model=ScriptResponse)
async def generate_script(request: VideoRequest):
    """
    Generate a video script based on the user's prompt.
    Returns a structured script with scenes, narration, and image prompts.
    """
    job_id = str(uuid.uuid4())
    
    try:
        # Initialize script generator
        generator = ScriptGenerator()
        
        # Update status: Generating script
        update_job_status(job_id, "generating_script", 10, "Generating video script...")
        
        # Generate script
        script = await generator.generate(
            prompt=request.prompt,
            duration=request.duration,
            style=request.style
        )
        
        update_job_status(job_id, "script_generated", 20, "Script generated successfully", {
            "title": script["title"],
            "scene_count": len(script["scenes"])
        })
        
        return ScriptResponse(
            job_id=job_id,
            title=script["title"],
            scenes=script["scenes"],
            total_duration=script["total_duration"]
        )
        
    except Exception as e:
        update_job_status(job_id, "error", 0, f"Script generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-images")
async def generate_images(request: dict):
    """
    Generate images for each scene based on the script.
    Takes a script response and generates corresponding images.
    """
    job_id = request.get("job_id", str(uuid.uuid4()))
    scenes = request.get("scenes", [])
    
    try:
        update_job_status(job_id, "generating_images", 25, "Generating scene images...")
        
        # Initialize image generator
        generator = ImageGenerator()
        
        # Generate images for each scene
        image_paths = []
        for i, scene in enumerate(scenes):
            update_job_status(job_id, "generating_images", 25 + (i * 10), f"Generating image {i+1}/{len(scenes)}...")
            image_path = await generator.generate_image(
                prompt=scene.get("image_prompt", scene.get("description", "")),
                scene_number=scene.get("scene_number", i + 1),
                job_id=job_id
            )
            image_paths.append(image_path)
        
        update_job_status(job_id, "images_generated", 50, "All images generated", {
            "images": image_paths
        })
        
        return {
            "job_id": job_id,
            "status": "images_generated",
            "images": image_paths
        }
        
    except Exception as e:
        update_job_status(job_id, "error", 0, f"Image generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-video")
async def generate_video(request: dict, background_tasks: BackgroundTasks):
    """
    Assemble the complete video from script and images.
    Returns the job ID for tracking progress.
    """
    job_id = request.get("job_id", str(uuid.uuid4()))
    script_data = request.get("script")
    image_paths = request.get("images", [])
    
    try:
        update_job_status(job_id, "assembling_video", 55, "Starting video assembly...")
        
        # Initialize video assembler
        assembler = VideoAssembler()
        
        # Run video assembly in background
        async def assemble_video():
            try:
                update_job_status(job_id, "assembling_video", 60, "Adding text overlays...")
                video_path = await assembler.assemble_video(
                    job_id=job_id,
                    script=script_data,
                    image_paths=image_paths
                )
                update_job_status(job_id, "completed", 100, "Video ready", {
                    "video_url": f"/output/{Path(video_path).name}"
                })
            except Exception as e:
                update_job_status(job_id, "error", 0, f"Video assembly failed: {str(e)}")
        
        # Start background task
        asyncio.create_task(assemble_video())
        
        return {
            "job_id": job_id,
            "status": "processing",
            "message": "Video generation in progress"
        }
        
    except Exception as e:
        update_job_status(job_id, "error", 0, f"Video assembly failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-video")
async def create_video(request: dict, background_tasks: BackgroundTasks):
    """
    Full pipeline: Generate script, images, and video in one call.
    """
    job_id = str(uuid.uuid4())
    prompt = request.get("prompt", "")
    duration = request.get("duration", 30)
    style = request.get("style", "cinematic")
    
    try:
        # Step 1: Generate script
        update_job_status(job_id, "generating_script", 5, "Generating video script...")
        script_gen = ScriptGenerator()
        script = await script_gen.generate(prompt=prompt, duration=duration, style=style)
        
        # Step 2: Generate images
        update_job_status(job_id, "generating_images", 30, "Generating scene images...")
        image_gen = ImageGenerator()
        image_paths = []
        
        for i, scene in enumerate(script["scenes"]):
            update_job_status(job_id, "generating_images", 30 + (i * 8), f"Generating image {i+1}/{len(script['scenes'])}...")
            image_path = await image_gen.generate_image(
                prompt=scene["image_prompt"],
                scene_number=scene["scene_number"],
                job_id=job_id
            )
            image_paths.append(image_path)
        
        # Step 3: Assemble video
        update_job_status(job_id, "assembling_video", 80, "Assembling video...")
        assembler = VideoAssembler()
        video_path = await assembler.assemble_video(
            job_id=job_id,
            script=script,
            image_paths=image_paths
        )
        
        update_job_status(job_id, "completed", 100, "Video ready", {
            "video_url": f"/output/{Path(video_path).name}"
        })
        
        return {
            "job_id": job_id,
            "status": "completed",
            "video_url": f"/output/{Path(video_path).name}",
            "script": script
        }
        
    except Exception as e:
        update_job_status(job_id, "error", 0, f"Video creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_video(filename: str):
    """Download a generated video file"""
    output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
    file_path = output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="video/mp4"
    )
