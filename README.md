# NSFW Video Analyzer Setup Guide

## Architecture Overview
- **Backend**: FastAPI with Python, handles all video processing and API calls
- **Frontend**: React app hosted separately on your Digital Ocean droplet
- **Video Processing**: FFmpeg for clips/frames extraction
- **Analysis Pipeline**: Gemini (primary) → Joy Caption + Grok (fallback)

## Backend Setup

### 1. Prerequisites
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nginx ffmpeg

# Create application directory
sudo mkdir -p /opt/nsfw-analyzer/backend
sudo chown -R $USER:$USER /opt/nsfw-analyzer
```

### 2. Setup Python Environment
```bash
cd /opt/nsfw-analyzer/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Copy your main.py and requirements.txt here
# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys
```bash
# Option 1: Update the systemd service file
sudo nano /etc/systemd/system/nsfw-analyzer.service
# Update the Environment variables with your actual API keys

# Option 2: Use a .env file
echo "GEMINI_API_KEY=your_key_here" >> .env
echo "REPLICATE_API_KEY=your_key_here" >> .env
echo "GROK_API_KEY=your_key_here" >> .env
```

### 4. Setup Systemd Service
```bash
# Copy the service file
sudo cp nsfw-analyzer.service /etc/systemd/system/

# Create log directory
sudo mkdir -p /var/log/nsfw-analyzer
sudo chown www-data:www-data /var/log/nsfw-analyzer

# Create temp directory
sudo mkdir -p /tmp/nsfw-analyzer
sudo chown www-data:www-data /tmp/nsfw-analyzer

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable nsfw-analyzer
sudo systemctl start nsfw-analyzer

# Check status
sudo systemctl status nsfw-analyzer
```

### 5. Configure Nginx
```bash
# Copy nginx config
sudo cp nsfw-analyzer.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/nsfw-analyzer.conf /etc/nginx/sites-enabled/

# Update the server_name in the config with your domain
sudo nano /etc/nginx/sites-available/nsfw-analyzer.conf

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL Certificate (if using HTTPS)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourdomain.com
```

## Frontend Setup

### 1. Build the React App
```bash
# On your local machine
cd frontend
npm install

# Update the API URL in the React app
echo "REACT_APP_API_URL=https://api.yourdomain.com" > .env

# Build
npm run build
```

### 2. Deploy to Digital Ocean Droplet
```bash
# Copy build files to your droplet
scp -r build/* user@your-droplet:/var/www/nsfw-analyzer/

# On the droplet, create nginx config for frontend
sudo nano /etc/nginx/sites-available/nsfw-analyzer-frontend.conf
```

Frontend nginx config:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/nsfw-analyzer;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## Testing

### 1. Test Backend Health
```bash
curl http://localhost:8005/health
# or
curl https://api.yourdomain.com/health
```

### 2. Test Analysis Endpoint
```bash
# Test with a small video file
curl -X POST -F "file=@test_video.mp4" https://api.yourdomain.com/analyze
```

### 3. Monitor Logs
```bash
# Service logs
sudo journalctl -u nsfw-analyzer -f

# Application logs
tail -f /var/log/nsfw-analyzer/nsfw-analyzer-*.log

# Nginx logs
tail -f /var/log/nginx/nsfw-analyzer-*.log
```

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check logs: `sudo journalctl -u nsfw-analyzer -n 50`
   - Verify Python path and virtual environment
   - Check file permissions

2. **FFmpeg errors**
   - Ensure ffmpeg is installed: `ffmpeg -version`
   - Check video codec support

3. **API errors**
   - Verify API keys are set correctly
   - Check rate limits on external APIs
   - Monitor quota usage

4. **Large video uploads fail**
   - Check nginx `client_max_body_size`
   - Verify timeout settings
   - Monitor disk space in `/tmp`

### Performance Tuning

1. **Increase workers** in systemd service:
   ```
   ExecStart=/opt/nsfw-analyzer/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8005 --workers 4
   ```

2. **Adjust timeouts** in nginx config for slow connections

3. **Enable caching** for static frontend assets

## Maintenance

### Update Backend
```bash
cd /opt/nsfw-analyzer/backend
git pull  # or copy new files
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart nsfw-analyzer
```

### View Metrics
```bash
# Check API usage
grep "analysis successful" /var/log/nsfw-analyzer/*.log | wc -l

# Check errors
grep "ERROR" /var/log/nsfw-analyzer/*.log

# Disk usage
du -sh /tmp/nsfw-analyzer
```

### Backup
```bash
# Backup logs
tar -czf nsfw-logs-$(date +%Y%m%d).tar.gz /var/log/nsfw-analyzer/

# Backup configuration
tar -czf nsfw-config-$(date +%Y%m%d).tar.gz /opt/nsfw-analyzer/backend/*.py /etc/nginx/sites-available/nsfw-analyzer.conf
```

## API Documentation

### POST /analyze
Upload a video for NSFW analysis.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (video file, max 60 seconds)

**Response:**
```json
{
  "method": "gemini|joycaption-grok",
  "is_nsfw": true|false,
  "category": "Safe|Violence|Sexual Content|Graphic Content|Hate Speech|Other",
  "explanation": "Detailed explanation...",
  "confidence": 0.95
}
```

### GET /health
Check service health and API key status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "services": {
    "gemini": true,
    "replicate": true,
    "grok": true
  }
}
```