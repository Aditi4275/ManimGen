"""
Render service for executing Manim scripts and generating videos.
"""
import os
import asyncio
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional

from config import get_settings

settings = get_settings()


async def render_scene(code: str, scene_id: str) -> Dict:
    """
    Render a Manim scene from code.
    
    Args:
        code: The Manim Python code to execute
        scene_id: Unique identifier for the scene
    
    Returns:
        Dict with video_url, thumbnail_url, and duration
    """
    # Create temporary directory for rendering
    temp_dir = tempfile.mkdtemp(prefix=f"manim_{scene_id}_")
    script_path = os.path.join(temp_dir, "scene.py")
    
    try:
        # Write code to temporary file
        with open(script_path, "w") as f:
            f.write(code)
        
        # Run Manim render command
        output_dir = os.path.join(temp_dir, "media")
        
        # Execute manim command
        process = await asyncio.create_subprocess_exec(
            "manim",
            "render",
            "-ql",  # Low quality for faster rendering (use -qh for high quality)
            "-o", f"{scene_id}",
            "--media_dir", output_dir,
            script_path,
            "GeneratedScene",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown render error"
            raise Exception(f"Manim render failed: {error_msg}")
        
        # Find the output video file
        video_file = None
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith(".mp4"):
                    video_file = os.path.join(root, file)
                    break
            if video_file:
                break
        
        if not video_file:
            raise Exception("No video file generated")
        
        # Copy video to output directory
        os.makedirs(settings.output_dir, exist_ok=True)
        output_filename = f"{scene_id}.mp4"
        output_path = os.path.join(settings.output_dir, output_filename)
        shutil.copy2(video_file, output_path)
        
        # Generate thumbnail (first frame)
        thumbnail_filename = f"{scene_id}_thumb.png"
        thumbnail_path = os.path.join(settings.output_dir, thumbnail_filename)
        
        await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-i", output_path,
            "-ss", "00:00:01",
            "-vframes", "1",
            "-y",
            thumbnail_path,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        # Get video duration
        duration = await get_video_duration(output_path)
        
        return {
            "video_url": f"/outputs/{output_filename}",
            "thumbnail_url": f"/outputs/{thumbnail_filename}" if os.path.exists(thumbnail_path) else None,
            "duration": duration
        }
        
    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)


async def get_video_duration(video_path: str) -> float:
    """Get the duration of a video file in seconds."""
    try:
        process = await asyncio.create_subprocess_exec(
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        stdout, _ = await process.communicate()
        return float(stdout.decode().strip())
    except:
        return 5.0  # Default duration


async def compile_project(
    scenes: List[Dict],
    project_id: str,
    audio_url: Optional[str] = None
) -> Dict:
    """
    Compile multiple scenes into a single video.
    
    Args:
        scenes: List of scene dictionaries with video_url
        project_id: Unique identifier for the project
        audio_url: Optional audio file to overlay
    
    Returns:
        Dict with video_url of the compiled video
    """
    if not scenes:
        raise Exception("No scenes to compile")
    
    temp_dir = tempfile.mkdtemp(prefix=f"compile_{project_id}_")
    
    # Get absolute path to output directory
    output_dir_abs = os.path.abspath(settings.output_dir)
    
    try:
        # Create file list for ffmpeg concat
        file_list_path = os.path.join(temp_dir, "files.txt")
        
        video_count = 0
        with open(file_list_path, "w") as f:
            for scene in scenes:
                video_url = scene.get("video_url")
                if video_url:
                    # Convert URL to absolute file path
                    video_path = os.path.join(
                        output_dir_abs,
                        os.path.basename(video_url)
                    )
                    if os.path.exists(video_path):
                        f.write(f"file '{video_path}'\n")
                        video_count += 1
        
        if video_count == 0:
            raise Exception("No rendered video files found to compile")
        
        # Output path
        output_filename = f"{project_id}_final.mp4"
        output_path = os.path.join(output_dir_abs, output_filename)
        temp_output = os.path.join(temp_dir, "combined.mp4")
        
        # Concatenate videos
        process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", file_list_path,
            "-c", "copy",
            "-y",
            temp_output,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        _, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Video concatenation failed: {stderr.decode()}")
        
        # Add audio if provided
        if audio_url:
            upload_dir_abs = os.path.abspath(settings.upload_dir)
            audio_path = os.path.join(
                upload_dir_abs,
                os.path.basename(audio_url)
            )
            
            if os.path.exists(audio_path):
                process = await asyncio.create_subprocess_exec(
                    "ffmpeg",
                    "-i", temp_output,
                    "-i", audio_path,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-shortest",
                    "-y",
                    output_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                await process.communicate()
            else:
                shutil.copy2(temp_output, output_path)
        else:
            shutil.copy2(temp_output, output_path)
        
        return {
            "video_url": f"/outputs/{output_filename}"
        }
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
