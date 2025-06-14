# NSFW Video Analyzer

AI-powered video content moderation system using advanced machine learning models.

## 🚀 Quick Start

1. **Backend Setup**: Follow [SETUP.md](SETUP.md) for complete backend deployment
2. **Frontend Setup**: See [frontend-setup.md](frontend-setup.md) for React app deployment
3. **Deployment**: Use [deployment-checklist.md](deployment-checklist.md) before going live

## 🏗️ Architecture

- **Backend**: FastAPI with Python
- **Frontend**: React with Tailwind CSS
- **Analysis Pipeline**: Gemini (primary) → Joy Caption + Grok (fallback)
- **Infrastructure**: Nginx, systemd, SSL/TLS

## 🔧 Key Features

- ✅ Multi-tier AI analysis system
- ✅ Video clip and frame extraction
- ✅ Real-time processing with progress tracking
- ✅ Confidence scoring and detailed explanations
- ✅ Production-ready deployment configs
- ✅ Comprehensive error handling and logging

## 📊 Analysis Methods

1. **Primary**: Google Gemini 2.5 Pro (direct video analysis)
2. **Fallback**: Joy Caption + Grok (frame-based analysis)

## 🛡️ Content Categories

- Safe
- Violence
- Sexual Content
- Graphic Content
- Hate Speech
- Other

## 📋 API Endpoints

- `POST /analyze` - Upload and analyze video
- `GET /health` - Service health check

## 🔑 Required API Keys

- Google Gemini API
- Replicate API (Joy Caption)
- Grok API (x.ai)

## 📚 Documentation

- [Complete Setup Guide](SETUP.md)
- [Frontend Deployment](frontend-setup.md)
- [Deployment Checklist](deployment-checklist.md)

## 🚨 Important Notes

- Maximum video duration: 60 seconds
- Supported formats: MP4, WebM, AVI, MOV
- Requires FFmpeg for video processing
- SSL/HTTPS recommended for production 