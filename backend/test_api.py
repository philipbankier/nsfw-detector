#!/usr/bin/env python3
"""
NSFW Video Analyzer API Test Script
Tests the health endpoint and video analysis functionality
"""

import sys
import requests
import json
import time
from pathlib import Path

def test_health(base_url):
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {data.get('status')}")
            print(f"   Services: {data.get('services')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False

def test_video_analysis(base_url, video_path):
    """Test video analysis endpoint"""
    print(f"🎥 Testing video analysis with: {video_path}")
    
    if not Path(video_path).exists():
        print(f"❌ Video file not found: {video_path}")
        return False
    
    try:
        with open(video_path, 'rb') as video_file:
            files = {'file': video_file}
            
            print("   Uploading video...")
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/analyze",
                files=files,
                timeout=300  # 5 minutes timeout
            )
            
            duration = time.time() - start_time
            print(f"   Analysis completed in {duration:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Video analysis successful!")
                print(f"   Method: {data.get('method')}")
                print(f"   NSFW: {data.get('is_nsfw')}")
                print(f"   Category: {data.get('category')}")
                print(f"   Confidence: {data.get('confidence')}")
                print(f"   Explanation: {data.get('explanation')[:100]}...")
                return True
            else:
                print(f"❌ Video analysis failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Video analysis error: {e}")
        return False

def create_test_video():
    """Create a simple test video using ffmpeg"""
    test_video_path = "test_video.mp4"
    
    if Path(test_video_path).exists():
        return test_video_path
    
    print("📹 Creating test video...")
    
    try:
        import subprocess
        
        # Create a 5-second test video with color bars
        cmd = [
            "ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=5:size=320x240:rate=30",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-y", test_video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Test video created: {test_video_path}")
            return test_video_path
        else:
            print(f"❌ Failed to create test video: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test video: {e}")
        return None

def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python3 test_api.py <base_url> [video_path]")
        print("Example: python3 test_api.py http://localhost:8005")
        print("Example: python3 test_api.py https://api.yourdomain.com sample.mp4")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    video_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🚀 Testing NSFW Video Analyzer API at: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    health_ok = test_health(base_url)
    
    if not health_ok:
        print("\n❌ Health check failed. Please check if the API is running.")
        sys.exit(1)
    
    # Test 2: Video analysis
    if video_path:
        print("\n" + "=" * 50)
        analysis_ok = test_video_analysis(base_url, video_path)
    else:
        # Try to create a test video
        print("\n" + "=" * 50)
        test_video = create_test_video()
        
        if test_video:
            analysis_ok = test_video_analysis(base_url, test_video)
        else:
            print("⚠️  No video provided and couldn't create test video")
            print("   Install ffmpeg or provide a video file path")
            analysis_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Video Analysis: {'✅ PASS' if analysis_ok else '❌ FAIL'}")
    
    if health_ok and analysis_ok:
        print("\n🎉 All tests passed! API is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the API configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main() 