import os
import logging
import tempfile
import subprocess
import base64
import json
import asyncio
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
import aiohttp
import cv2
import numpy as np
from PIL import Image
import io
import replicate
import google.generativeai as genai
from dotenv import load_dotenv
import whisper

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

# Initialize Whisper model
whisper_model = None

def get_whisper_model():
    """Get or initialize Whisper model"""
    global whisper_model
    if whisper_model is None:
        logger.info("Loading Whisper base.en model...")
        whisper_model = whisper.load_model("base.en")
        logger.info("Whisper model loaded successfully")
    return whisper_model

# Response Models
class AnalysisResult(BaseModel):
    method: str
    status: str  # "safe" or "nsfw"
    categories: List[str]  # ["pornography", "violence", "self-harm", "weapons", "profanity", "other"]
    severity: int  # 0-5
    description: str  # Brief 1-2 sentence description

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

class GeminiResponse(BaseModel):
    status: Literal["safe", "nsfw"]
    categories: List[str]
    severity: int = Field(ge=0, le=5)
    description: str
    
    @field_validator('categories')
    @classmethod
    def validate_categories(cls, v):
        valid_categories = {'pornography', 'violence', 'self-harm', 'weapons', 'profanity', 'other'}
        # Filter to only valid categories
        filtered_categories = [cat for cat in v if cat in valid_categories]
        # If no valid categories found, default to 'other'
        if not filtered_categories:
            return ['other']
        return filtered_categories

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

def extract_json_from_markdown(text: str) -> str:
    """Extract JSON from markdown code blocks"""
    # Remove markdown code blocks if present
    if "```json" in text:
        # Find the JSON content between ```json and ```
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()
    elif "```" in text:
        # Handle generic code blocks
        start = text.find("```") + 3
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()
    
    # Return original text if no code blocks found
    return text.strip()

async def analyze_with_gemini(video_clips: List[str]) -> Optional[AnalysisResult]:
    """Analyze video clips using Google Gemini API"""
    if not GEMINI_API_KEY:
        logger.error("Gemini API key not configured")
        return None
    
    logger.info("Starting Gemini analysis")
    
    try:
        # Get the model
        model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06')
        
        # Prepare the prompt
        prompt = """You are a strict content-safety engine. Analyze the video content and determine if it's safe or NSFW.

IMPORTANT: If you detect ANY profanity, swearing, strong language, or curse words (including implied, censored, or abbreviated forms), you MUST categorize it as "profanity".

Return your analysis in this exact JSON format (no markdown, just pure JSON):
{
    "status": "safe" or "nsfw",
    "categories": ["pornography", "violence", "self-harm", "weapons", "profanity", "other"],
    "severity": 0-5,
    "description": "brief 1-2 sentence description"
}

Severity scale:
0 = safe content
1 = suggestive
2 = mature
3 = explicit
4 = extreme
5 = illegal

Categories (choose ALL that apply):
- pornography (sexual/nudity)
- violence (harm/gore)
- self-harm (suicide/injury)
- weapons (guns/knives/explosives)
- profanity (ANY strong language, swearing, curse words, f-words, s-words, etc.)
- other (hate speech/drugs/disturbing content that doesn't fit above)

CRITICAL: If you mention profanity, swearing, strong language, or curse words in your description, you MUST include "profanity" in the categories array.

Multiple categories allowed if applicable."""
        
        # Process each clip
        results = []
        for i, clip in enumerate(video_clips):
            try:
                # Convert base64 to bytes
                video_bytes = base64.b64decode(clip)
                
                # Create content parts
                content = [
                    prompt,
                    {
                        "mime_type": "video/mp4",
                        "data": video_bytes
                    }
                ]
                
                # Generate content
                response = model.generate_content(content)
                
                if response and response.text:
                    # Extract JSON from markdown if needed
                    json_text = extract_json_from_markdown(response.text)
                    logger.info(f"Extracted JSON for clip {i}: {json_text[:200]}...")
                    
                    # Parse JSON response
                    try:
                        # Log the raw JSON before parsing
                        logger.info(f"Raw JSON response for clip {i}: {json_text}")
                        
                        result = GeminiResponse.model_validate_json(json_text)
                        
                        # Log the parsed result
                        logger.info(f"Parsed result for clip {i}: status={result.status}, categories={result.categories}, severity={result.severity}")
                        
                        results.append(result)
                        logger.info(f"Successfully parsed clip {i} result")
                    except Exception as e:
                        logger.error(f"Failed to parse Gemini response for clip {i}: {e}")
                        logger.error(f"Raw response: {response.text}")
                        continue
                
            except Exception as e:
                logger.error(f"Error processing clip {i}: {e}")
                continue
        
        if not results:
            logger.error("No valid results from Gemini analysis")
            return None
        
        # Combine results (take the most severe result)
        final_result = max(results, key=lambda x: x.severity)
        
        analysis_result = AnalysisResult(
            method="gemini",
            status=final_result.status,
            categories=final_result.categories,
            severity=final_result.severity,
            description=final_result.description
        )
        
        logger.info(f"Final AnalysisResult: status={analysis_result.status}, categories={analysis_result.categories}, severity={analysis_result.severity}")
        return analysis_result
        
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

async def analyze_with_grok(analysis_texts: List[str]) -> Optional[AnalysisResult]:
    """Analyze combined visual and audio content using Grok API"""
    if not GROK_API_KEY:
        logger.error("Grok API key not configured")
        return None
    
    logger.info("Starting Grok analysis")
    
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Combine all analysis texts
    combined_text = "\n\n".join(analysis_texts)
    
    payload = {
        "model": "grok-3-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a strict content-safety engine. Analyze the combined visual and audio content. "
                "Return JSON exactly: "
                "{\"status\":\"safe\"|\"nsfw\", \"categories\":[\"pornography\"|\"violence\"|\"self-harm\"|\"weapons\"|\"profanity\"|\"other\"], "
                "\"severity\":0-5, \"description\":\"brief 1-2 sentence description\"}. "
                "Severity scale: 0=safe content, 1=suggestive, 2=mature, 3=explicit, 4=extreme, 5=illegal. "
                "Categories: pornography (sexual/nudity), violence (harm/gore), self-harm (suicide/injury), "
                "weapons (guns/knives/explosives), profanity (strong language/swearing), other (hate/drugs/disturbing). "
                "Multiple categories allowed if applicable. "
                "Consider both visual descriptions and audio transcript in your analysis."
            },
            {
                "role": "user",
                "content": f"Analyze this content:\n\n{combined_text}"
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
                    result = GeminiResponse.model_validate_json(content)
                    return AnalysisResult(
                        method="joycaption-whisper-grok",
                        status=result.status,
                        categories=result.categories,
                        severity=result.severity,
                        description=result.description
                    )
                except Exception as e:
                    logger.error(f"Failed to parse Grok response: {e}")
                    return None
    
    except Exception as e:
        logger.error(f"Grok analysis failed: {e}")
        return None

async def transcribe_audio(video_path: str) -> Optional[str]:
    """Extract and transcribe audio from video using Whisper"""
    try:
        # Extract audio to temporary file
        temp_audio = os.path.join(TEMP_DIR, f"audio_{datetime.now().timestamp()}.wav")
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn",  # No video
            "-acodec", "pcm_s16le",  # PCM 16-bit
            "-ar", "16000",  # 16kHz sample rate
            "-ac", "1",  # Mono
            "-y", temp_audio
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error extracting audio: {e}")
            return None
        
        # Run Whisper in thread pool
        loop = asyncio.get_event_loop()
        
        def run_whisper():
            model = get_whisper_model()
            result = model.transcribe(temp_audio)
            return result["text"]
        
        transcript = await loop.run_in_executor(None, run_whisper)
        
        # Clean up
        os.unlink(temp_audio)
        
        return transcript.strip() if transcript else None
        
    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        return None

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
                logger.info(f"Gemini analysis successful: {result.status}")
                return result
        
        # Step 2: Fallback to Joy Caption + Whisper + Grok
        logger.info("Falling back to Joy Caption + Whisper + Grok analysis")
        
        # Get visual analysis from frames
        frames = await extract_video_frames(temp_file_path, num_frames=3)
        if not frames:
            raise HTTPException(status_code=500, detail="Failed to extract frames from video")
        
        # Get audio analysis from Whisper
        transcript = await transcribe_audio(temp_file_path)
        
        # Analyze frames with Joy Caption
        captions = []
        for i, frame in enumerate(frames):
            logger.info(f"Analyzing frame {i+1}/{len(frames)} with Joy Caption")
            caption = await analyze_with_joy_caption(frame)
            if caption:
                captions.append(caption)
        
        if not captions:
            raise HTTPException(status_code=500, detail="Failed to generate captions for frames")
        
        # Combine visual and audio analysis for Grok
        analysis_text = "\n\n".join([
            "Visual Analysis:",
            *[f"Frame {i+1}: {caption}" for i, caption in enumerate(captions)],
            "\nAudio Analysis:",
            transcript if transcript else "No audio transcript available"
        ])
        
        # Analyze combined content with Grok
        result = await analyze_with_grok([analysis_text])  # Pass as single item list
        if result:
            logger.info(f"Grok analysis successful: {result.status}")
            return result
        
        # If all methods fail, return error
        raise HTTPException(
            status_code=500,
            detail="All analysis methods failed. Please try again later."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
    
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