# Complete NSFW Video Analyzer Setup Guide

## Prerequisites
- Ubuntu 22.04+ server with at least 2GB RAM
- Domain name (optional but recommended)
- API keys for: Google Gemini, Replicate, and Grok (x.ai)

## Project Structure Setup

### 1. Clone or Create Project Structure
```bash
# Create main project directory
mkdir -p ~/nsfw-video-analyzer
cd ~/nsfw-video-analyzer

# Create subdirectories
mkdir -p backend frontend deployment/nginx deployment/systemd docs
```

### 2. Backend Files Setup
Place these files in the `backend/` directory:
- `main.py` - FastAPI application
- `requirements.txt` - Python dependencies
- `.env.example` - Environment template
- `test_api.py` - Testing script
- `setup.sh` - Automated setup

```bash
# Create .env from template
cd backend
cp .env.example .env
# Edit .env and add your API keys
nano .env
```

### 3. Frontend Files Setup
Place these files in the `frontend/` directory:

#### In `frontend/public/`:
- `index.html`

#### In `frontend/src/`:
- `App.js` - Main React component
- `index.js` - React entry point
- `index.css` - Tailwind CSS

#### In `frontend/`:
- `package.json`
- `tailwind.config.js`
- `.env.example`
- `.gitignore`

```bash
# Setup frontend environment
cd frontend
cp .env.example .env
# Edit .env to set your backend URL
nano .env
```

## Backend Deployment

### 1. Run Automated Setup
```bash
cd ~/nsfw-video-analyzer/backend
chmod +x setup.sh
./setup.sh
```

### 2. Configure API Keys
```bash
# Edit the .env file
sudo nano /opt/nsfw-analyzer/backend/.env
```

Add your actual API keys:
```env
GEMINI_API_KEY=your_actual_gemini_key
REPLICATE_API_KEY=your_actual_replicate_key
GROK_API_KEY=your_actual_grok_key
```

### 3. Restart Service
```bash
sudo systemctl restart nsfw-analyzer
sudo systemctl status nsfw-analyzer
```

### 4. Configure Nginx for Backend
```bash
# Copy backend nginx config
sudo cp ~/nsfw-video-analyzer/deployment/nginx/nsfw-analyzer-backend.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/nsfw-analyzer-backend.conf /etc/nginx/sites-enabled/

# Edit to add your domain
sudo nano /etc/nginx/sites-available/nsfw-analyzer-backend.conf
# Replace api.yourdomain.com with your actual domain

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Setup SSL for Backend
```bash
sudo certbot --nginx -d api.yourdomain.com
```

## Frontend Deployment

### 1. Build Frontend Locally
```bash
cd ~/nsfw-video-analyzer/frontend

# Install dependencies
npm install

# Build for production
npm run build
```

### 2. Deploy to Server
```bash
# Create web directory
sudo mkdir -p /var/www/nsfw-analyzer

# Copy build files
sudo cp -r build/* /var/www/nsfw-analyzer/

# Set permissions
sudo chown -R www-data:www-data /var/www/nsfw-analyzer
```

### 3. Configure Nginx for Frontend
```bash
# Copy frontend nginx config
sudo cp ~/nsfw-video-analyzer/deployment/nginx/nsfw-analyzer-frontend.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/nsfw-analyzer-frontend.conf /etc/nginx/sites-enabled/

# Edit to add your domain
sudo nano /etc/nginx/sites-available/nsfw-analyzer-frontend.conf
# Replace yourdomain.com with your actual domain
# Update api.yourdomain.com in CSP header

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Setup SSL for Frontend
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Testing the Deployment

### 1. Test Backend API
```bash
# Test health endpoint
curl https://api.yourdomain.com/health

# Test with sample video
cd ~/nsfw-video-analyzer/backend
python3 test_api.py sample_video.mp4 https://api.yourdomain.com
```

### 2. Test Frontend
- Navigate to https://yourdomain.com
- Upload a test video
- Verify results display correctly

## Directory Structure After Deployment

```
# Development machine
~/nsfw-video-analyzer/
├── backend/
├── frontend/
├── deployment/
└── docs/

# Server directories
/opt/nsfw-analyzer/backend/       # Backend application
/var/www/nsfw-analyzer/           # Frontend files
/var/log/nsfw-analyzer/           # Log files
/tmp/nsfw-analyzer/               # Temporary video files
```

## Common Commands

### Backend Management
```bash
# Service control
sudo systemctl start|stop|restart|status nsfw-analyzer

# View logs
sudo journalctl -u nsfw-analyzer -f
tail -f /var/log/nsfw-analyzer/*.log

# Update backend
cd /opt/nsfw-analyzer/backend
source venv/bin/activate
git pull  # or copy new files
pip install -r requirements.txt
sudo systemctl restart nsfw-analyzer
```

### Frontend Updates
```bash
# Build new version locally
cd ~/nsfw-video-analyzer/frontend
npm run build

# Deploy update
sudo rm -rf /var/www/nsfw-analyzer/*
sudo cp -r build/* /var/www/nsfw-analyzer/
sudo chown -R www-data:www-data /var/www/nsfw-analyzer
```

### Monitoring
```bash
# Check disk usage
df -h
du -sh /tmp/nsfw-analyzer

# Check API endpoints
curl https://api.yourdomain.com/health

# Monitor nginx
tail -f /var/log/nginx/nsfw-analyzer-*.log
```

## Troubleshooting

### Backend Issues
1. **Service won't start**: Check `sudo journalctl -u nsfw-analyzer -n 100`
2. **API key errors**: Verify `.env` file has correct keys
3. **FFmpeg errors**: Ensure `ffmpeg -version` works

### Frontend Issues
1. **CORS errors**: Check backend CORS settings and frontend API URL
2. **404 errors**: Verify nginx config and file permissions
3. **Upload failures**: Check nginx `client_max_body_size`

### Performance Tuning
1. Increase backend workers in systemd service file
2. Enable nginx caching for static assets
3. Use CDN for frontend assets (optional)

## Security Checklist
- [ ] API keys in `.env` files only
- [ ] HTTPS enabled for both frontend and backend
- [ ] Firewall configured (allow 80, 443, 22)
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`

## Backup Recommendations
1. Backup `.env` files securely
2. Backup nginx configurations
3. Create AMI/snapshot of configured server
4. Document any custom configurations