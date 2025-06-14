import os
import logging
import tempfile
import subprocess
import base64
import json
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiohttp
import cv2
import numpy as np
from PIL import Image
import io
import replicate
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure replicate API token
replicate_key = os.getenv("REPLICATE_API_KEY")
if replicate_key:
    # Set both the environment variable and the replicate.api_token
    os.environ["REPLICATE_API_TOKEN"] = replicate_key
    replicate.api_token = replicate_key
    print(f"✅ Replicate API token configured (length: {len(replicate_key)})")
else:
    print("❌ Replicate API token not found in environment")

# Configure logging
log_dir = Path(os.getenv("LOG_DIR", "./logs"))
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"nsfw-analyzer-{datetime.now().strftime('%Y-%m-%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="NSFW Video Analyzer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MAX_VIDEO_DURATION = 60  # seconds
TEMP_DIR = os.getenv("TEMP_DIR", "./temp")
Path(TEMP_DIR).mkdir(exist_ok=True)

# API Keys - Load from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "")

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("✅ Gemini API configured")
else:
    logger.warning("❌ Gemini API key not found")

# Response Models
class AnalysisResult(BaseModel):
    method: str
    is_nsfw: bool
    category: str
    explanation: str
    confidence: Optional[float] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

# Utility Functions
async def get_video_duration(file_path: str) -> float:
    """Get video duration using ffprobe"""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except Exception as e:
        logger.error(f"Error getting video duration: {e}")
        return 0

async def extract_video_clips(file_path: str, num_clips: int = 3) -> List[str]:
    """Extract clips from video at different timestamps"""
    clips = []
    duration = await get_video_duration(file_path)
    
    if duration <= 0:
        raise ValueError("Invalid video duration")
    
    # Calculate timestamps for clips
    clip_duration = min(2, duration / num_clips)  # 2 seconds per clip or less
    timestamps = [
        0,  # Start
        duration / 2 - clip_duration / 2,  # Middle
        max(0, duration - clip_duration)  # End
    ]
    
    for i, start_time in enumerate(timestamps):
        output_path = os.path.join(TEMP_DIR, f"clip_{i}_{datetime.now().timestamp()}.mp4")
        
        cmd = [
            "ffmpeg", "-i", file_path,
            "-ss", str(start_time),
            "-t", str(clip_duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-strict", "experimental",
            "-y", output_path
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            
            # Convert to base64
            with open(output_path, "rb") as f:
                clip_base64 = base64.b64encode(f.read()).decode('utf-8')
                clips.append(clip_base64)
            
            # Clean up
            os.unlink(output_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error extracting clip {i}: {e}")
            continue
    
    return clips

async def extract_video_frames(file_path: str, num_frames: int = 5) -> List[str]:
    """Extract frames from video at even intervals"""
    frames = []
    cap = cv2.VideoCapture(file_path)
    
    try:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            raise ValueError("Invalid video frame count")
        
        # Calculate frame indices to extract
        indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            
            if ret:
                # Convert frame to base64
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                frames.append(frame_base64)
            else:
                logger.warning(f"Failed to extract frame at index {idx}")
    
    finally:
        cap.release()
    
    return frames

async def analyze_with_gemini(video_clips: List[str]) -> Optional[AnalysisResult]:
    """Analyze video clips using Google Gemini API"""
    if not GEMINI_API_KEY:
        logger.error("Gemini API key not configured")
        return None
    
    logger.info("Starting Gemini analysis")
    
    try:
        # Get the model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Prepare the content parts
        parts = [
            "Analyze this video content and determine: 1) Is it NSFW? 2) What category does it fall into? Categories: Safe, Violence, Sexual Content, Graphic Content, Hate Speech, Other. Provide a confidence score (0-1) and brief explanation. Format your response as JSON with keys: is_nsfw (boolean), category (string), confidence (float), explanation (string)"
        ]
        
        # Add video clips as base64 data
        for i, clip in enumerate(video_clips):
            parts.append({
                "mime_type": "video/mp4",
                "data": clip
            })
        
        # Run in thread pool to avoid blocking the async event loop
        import asyncio
        loop = asyncio.get_event_loop()
        
        def run_gemini():
            return model.generate_content(parts)
        
        response = await loop.run_in_executor(None, run_gemini)
        
        if not response or not response.text:
            logger.error("Empty response from Gemini")
            return None
        
        content = response.text
        logger.info(f"Gemini response: {content[:200]}...")
        
        # Try to parse as JSON - handle markdown code blocks
        try:
            # Remove markdown code blocks if present
            json_content = content.strip()
            
            # Handle markdown code blocks
            if '```json' in json_content:
                # Extract JSON from ```json blocks
                start = json_content.find('```json') + 7
                end = json_content.find('```', start)
                if end != -1:
                    json_content = json_content[start:end].strip()
            elif '```' in json_content:
                # Handle generic code blocks
                start = json_content.find('```') + 3
                end = json_content.find('```', start)
                if end != -1:
                    json_content = json_content[start:end].strip()
            
            # Try to find JSON within the content if it's not in code blocks
            if not json_content.startswith('{'):
                # Look for JSON object in the content
                start_brace = json_content.find('{')
                if start_brace != -1:
                    # Find the matching closing brace
                    brace_count = 0
                    end_brace = start_brace
                    for i, char in enumerate(json_content[start_brace:], start_brace):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_brace = i + 1
                                break
                    json_content = json_content[start_brace:end_brace]
            
            logger.info(f"Extracted JSON content: {json_content}")
            result_json = json.loads(json_content)
            logger.info(f"Parsed JSON: {result_json}")
            
            analysis_result = AnalysisResult(
                method="gemini",
                is_nsfw=result_json.get('is_nsfw', False),
                category=result_json.get('category', 'Unknown'),
                explanation=result_json.get('explanation', ''),
                confidence=result_json.get('confidence', 0.5)
            )
            
            logger.info(f"Final AnalysisResult: is_nsfw={analysis_result.is_nsfw}, category={analysis_result.category}")
            return analysis_result
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}, content: {content}")
            # Fallback parsing
            is_nsfw = 'nsfw' in content.lower() and 'not nsfw' not in content.lower()
            category = extract_category_from_text(content)
            
            return AnalysisResult(
                method="gemini",
                is_nsfw=is_nsfw,
                category=category,
                explanation=content
            )
    
    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        return None

async def analyze_with_joy_caption(frame_base64: str) -> Optional[str]:
    """Analyze a single frame using Joy Caption on Replicate"""
    if not REPLICATE_API_KEY:
        logger.error("Replicate API key not configured")
        return None
    
    logger.info(f"Joy Caption: API key present: {bool(REPLICATE_API_KEY)}, replicate.api_token set: {bool(replicate.api_token)}")
    
    try:
        # Run Joy Caption model
        input_data = {
            "image": f"data:image/jpeg;base64,{frame_base64}"
        }
        
        logger.info(f"Calling replicate with model: pipi32167/joy-caption")
        logger.info(f"Input data keys: {list(input_data.keys())}")
        
        # Run the model in thread pool to avoid blocking the async event loop
        import asyncio
        loop = asyncio.get_event_loop()
        
        def run_replicate():
            # Ensure token is set in this thread
            if not replicate.api_token and os.getenv("REPLICATE_API_TOKEN"):
                replicate.api_token = os.getenv("REPLICATE_API_TOKEN")
            
            return replicate.run(
                "pipi32167/joy-caption:86674ddd559dbdde6ed40e0bdfc0720c84d82971e288149fcf2c35c538272617",
                input=input_data
            )
        
        output = await loop.run_in_executor(None, run_replicate)
        
        logger.info(f"Joy Caption output type: {type(output)}, length: {len(str(output)) if output else 0}")
        return output
        
    except Exception as e:
        logger.error(f"Joy Caption analysis failed: {e}")
        return None

async def analyze_with_grok(captions: List[str]) -> Optional[AnalysisResult]:
    """Analyze frame captions using Grok API"""
    if not GROK_API_KEY:
        logger.error("Grok API key not configured")
        return None
    
    logger.info("Starting Grok analysis")
    
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare captions text
    captions_text = "\n\n".join([f"Frame {i+1}: {caption}" for i, caption in enumerate(captions)])
    
    payload = {
        "model": "grok-3-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are analyzing image descriptions to determine if video content is NSFW. Categorize as: Safe, Violence, Sexual Content, Graphic Content, Hate Speech, or Other. Respond in JSON format with keys: is_nsfw (boolean), category (string), confidence (float 0-1), explanation (string)"
            },
            {
                "role": "user",
                "content": f"Analyze these frame descriptions from a video and determine if it's NSFW:\n\n{captions_text}"
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    logger.error(f"Grok API error: {response.status}")
                    return None
                
                data = await response.json()
                content = data['choices'][0]['message']['content']
                
                # Parse JSON response
                try:
                    result_json = json.loads(content)
                    return AnalysisResult(
                        method="joycaption-grok",
                        is_nsfw=result_json.get('is_nsfw', False),
                        category=result_json.get('category', 'Unknown'),
                        explanation=result_json.get('explanation', ''),
                        confidence=result_json.get('confidence', 0.5)
                    )
                except json.JSONDecodeError:
                    # Fallback parsing
                    is_nsfw = 'nsfw' in content.lower() and 'not nsfw' not in content.lower()
                    category = extract_category_from_text(content)
                    
                    return AnalysisResult(
                        method="joycaption-grok",
                        is_nsfw=is_nsfw,
                        category=category,
                        explanation=content
                    )
    
    except Exception as e:
        logger.error(f"Grok analysis failed: {e}")
        return None

def extract_category_from_text(text: str) -> str:
    """Extract category from text response"""
    categories = ['Safe', 'Violence', 'Sexual Content', 'Graphic Content', 'Hate Speech', 'Other']
    text_lower = text.lower()
    
    for category in categories:
        if category.lower() in text_lower:
            return category
    
    return 'Other'

# API Endpoints
@app.post("/analyze", response_model=AnalysisResult)
async def analyze_video(file: UploadFile = File(...)):
    """Main endpoint to analyze uploaded video"""
    temp_file_path = None
    
    try:
        # Log request
        logger.info(f"Received video for analysis: {file.filename}, size: {file.size}")
        
        # Save uploaded file
        temp_file_path = os.path.join(TEMP_DIR, f"{datetime.now().timestamp()}_{file.filename}")
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Check video duration and trim if necessary
        duration = await get_video_duration(temp_file_path)
        logger.info(f"Original video duration: {duration}s")
        
        if duration > MAX_VIDEO_DURATION:
            logger.info(f"Video is {duration}s, trimming to first {MAX_VIDEO_DURATION}s for analysis")
            # Create trimmed version
            trimmed_file_path = os.path.join(TEMP_DIR, f"trimmed_{datetime.now().timestamp()}_{file.filename}")
            
            cmd = [
                "ffmpeg", "-i", temp_file_path,
                "-t", str(MAX_VIDEO_DURATION),  # Trim to first 60 seconds
                "-c", "copy",  # Copy streams without re-encoding for speed
                "-y", trimmed_file_path
            ]
            
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                # Replace original with trimmed version
                os.unlink(temp_file_path)
                temp_file_path = trimmed_file_path
                logger.info(f"Successfully trimmed video to {MAX_VIDEO_DURATION}s")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error trimming video: {e}")
                # Continue with original video if trimming fails
                if os.path.exists(trimmed_file_path):
                    os.unlink(trimmed_file_path)
        
        # Step 1: Try Gemini analysis
        video_clips = await extract_video_clips(temp_file_path)
        if video_clips:
            result = await analyze_with_gemini(video_clips)
            if result:
                logger.info(f"Gemini analysis successful: {result.category}")
                return result
        
        # Step 2: Fallback to Joy Caption + Grok
        logger.info("Falling back to Joy Caption + Grok analysis")
        frames = await extract_video_frames(temp_file_path, num_frames=3)  # Reduced to 3 frames for testing
        
        if not frames:
            raise HTTPException(status_code=500, detail="Failed to extract frames from video")
        
        # Analyze frames with Joy Caption
        captions = []
        for i, frame in enumerate(frames):
            logger.info(f"Analyzing frame {i+1}/{len(frames)} with Joy Caption")
            caption = await analyze_with_joy_caption(frame)
            if caption:
                captions.append(caption)
        
        if not captions:
            raise HTTPException(status_code=500, detail="Failed to generate captions for frames")
        
        # Analyze captions with Grok
        result = await analyze_with_grok(captions)
        if result:
            logger.info(f"Grok analysis successful: {result.category}")
            return result
        
        # If all methods fail
        raise HTTPException(status_code=500, detail="All analysis methods failed")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "gemini": bool(GEMINI_API_KEY),
            "replicate": bool(REPLICATE_API_KEY),
            "grok": bool(GROK_API_KEY)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)