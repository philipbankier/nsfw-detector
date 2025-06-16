# NSFW Video Analyzer

AI-powered video content moderation system using advanced machine learning models.

## 🌟 Features

- **Multi-tier Analysis**: Combines Gemini, Joy Caption, and Grok for comprehensive content detection
- **Real-time Processing**: Analyzes videos up to 60 seconds in length
- **Modern UI**: Beautiful, responsive interface built with React and Tailwind CSS
- **Production Ready**: Complete deployment configuration with Nginx and systemd
- **Comprehensive Testing**: Full test suite for both frontend and backend
- **Detailed Documentation**: Complete setup, deployment, and maintenance guides

## 🏗️ Architecture

### Backend
- FastAPI application with Python 3.11+
- Multi-tier analysis pipeline:
  1. Primary: Google Gemini 2.5 Pro
  2. Fallback: Joy Caption + Grok
- FFmpeg for video processing
- Comprehensive error handling and logging

### Frontend
- React 18 with Tailwind CSS
- Modern, responsive design
- Real-time upload and analysis
- Detailed results display
- Error handling and loading states

## 🚀 Quick Start

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/nsfw-video-analyzer.git
cd nsfw-video-analyzer
```

2. **Backend Setup**
```bash
cd backend
cp .env.example .env  # Add your API keys
./setup.sh
```

3. **Frontend Setup**
```bash
cd frontend
cp .env.example .env  # Set your backend URL
npm install
npm start
```

4. **Access the Application**
- Frontend: http://localhost:3005
- Backend API: http://localhost:8005

## 📚 Documentation

- [Complete Setup Guide](docs/SETUP.md)
- [Frontend Deployment](docs/frontend-setup.md)
- [Deployment Checklist](docs/deployment-checklist.md)
- [Final Checklist](docs/FINAL_CHECKLIST.md)

## 🔧 Requirements

### Backend
- Python 3.11+
- FFmpeg
- API Keys:
  - Google Gemini
  - Replicate (Joy Caption)
  - Grok (x.ai)

### Frontend
- Node.js 16+
- npm 8+

### Server
- Ubuntu 22.04+
- 2GB+ RAM
- Nginx
- SSL certificate (recommended)

## 🛡️ Security

- HTTPS enforcement
- API key protection
- Input validation
- File type verification
- Rate limiting
- CORS configuration
- Content Security Policy

## 📊 Monitoring

- Service health checks
- Resource usage tracking
- Error logging
- Performance metrics
- User feedback collection

## 🔄 Maintenance

### Regular Tasks
- Dependency updates
- Security patches
- Log rotation
- Backup verification
- Performance monitoring

### Emergency Procedures
- Rollback procedures
- Incident response
- Support contacts
- Status page
- Communication plan

## 🎯 Testing

### Backend Tests
```bash
cd backend
python3 test_api.py
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

- GitHub Issues
- Documentation
- Email support (optional)

## 🎉 Acknowledgments

- Google Gemini API
- Replicate (Joy Caption)
- Grok (x.ai)
- FastAPI
- React
- Tailwind CSS
- FFmpeg

---

## 🔍 Final Notes

- Maximum video duration: 60 seconds
- Supported formats: MP4, WebM, AVI, MOV
- Requires FFmpeg for video processing
- SSL/HTTPS recommended for production
- Regular backups recommended
- Monitor resource usage
- Keep dependencies updated