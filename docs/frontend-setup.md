# Frontend Setup Guide

Complete guide for building and deploying the NSFW Video Analyzer React frontend.

## 📋 Prerequisites

- Node.js 16+ and npm
- Backend API running (see [SETUP.md](SETUP.md))
- Domain name (optional but recommended)

## 🏗️ Local Development Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
```

Set your backend URL:
```env
# For local development
REACT_APP_API_URL=http://localhost:8005

# For production
REACT_APP_API_URL=https://api.yourdomain.com
```

### 3. Start Development Server
```bash
npm start
```

The app will be available at `http://localhost:3005`

## 🚀 Production Build

### 1. Build for Production
```bash
# Ensure production API URL is set in .env
echo "REACT_APP_API_URL=https://api.yourdomain.com" > .env

# Build the app
npm run build
```

### 2. Test Build Locally (Optional)
```bash
# Install serve globally
npm install -g serve

# Serve the build
serve -s build -l 3000
```

## 🌐 Deployment to Server

### Option 1: Direct Upload
```bash
# From your local machine
scp -r build/* user@your-server:/var/www/nsfw-analyzer/
```

### Option 2: Git-based Deployment
```bash
# On your server
cd /var/www/nsfw-analyzer
git pull origin main
npm install
npm run build
```

### 3. Set Proper Permissions
```bash
# On your server
sudo chown -R www-data:www-data /var/www/nsfw-analyzer
sudo chmod -R 755 /var/www/nsfw-analyzer
```

## ⚙️ Nginx Configuration

### 1. Copy Nginx Config
```bash
sudo cp deployment/nginx/nsfw-analyzer-frontend.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/nsfw-analyzer-frontend.conf /etc/nginx/sites-enabled/
```

### 2. Update Domain Names
```bash
sudo nano /etc/nginx/sites-available/nsfw-analyzer-frontend.conf
```

Replace `yourdomain.com` with your actual domain:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

Also update the CSP header to match your backend domain:
```nginx
connect-src 'self' https://api.yourdomain.com;
```

### 3. Test and Reload Nginx
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 SSL Certificate Setup

### 1. Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### 2. Get SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 3. Test Auto-renewal
```bash
sudo certbot renew --dry-run
```

## 🧪 Testing the Frontend

### 1. Basic Functionality Test
- Navigate to your domain
- Check if the upload interface loads
- Verify drag-and-drop functionality
- Test file selection

### 2. API Integration Test
- Upload a small test video
- Verify the analysis request is sent
- Check if results display correctly
- Test error handling with invalid files

### 3. Browser Compatibility
Test in major browsers:
- Chrome/Chromium
- Firefox
- Safari
- Edge

## 🔧 Troubleshooting

### Common Issues

#### 1. CORS Errors
**Problem**: Frontend can't connect to backend
**Solution**: 
- Check backend CORS settings in `main.py`
- Verify `REACT_APP_API_URL` is correct
- Ensure backend is running and accessible

#### 2. Build Errors
**Problem**: `npm run build` fails
**Solution**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### 3. 404 Errors on Refresh
**Problem**: React Router routes return 404
**Solution**: Verify nginx config has:
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

#### 4. Slow Loading
**Problem**: App loads slowly
**Solutions**:
- Enable gzip compression in nginx
- Use CDN for static assets
- Optimize images and icons

### Performance Optimization

#### 1. Enable Compression
Already configured in nginx config:
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

#### 2. Cache Static Assets
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

#### 3. Monitor Bundle Size
```bash
# Analyze bundle size
npm install -g webpack-bundle-analyzer
npx webpack-bundle-analyzer build/static/js/*.js
```

## 🔄 Updates and Maintenance

### 1. Update Frontend
```bash
# Local development
git pull origin main
npm install
npm run build

# Deploy to server
scp -r build/* user@server:/var/www/nsfw-analyzer/
```

### 2. Monitor Logs
```bash
# Nginx access logs
tail -f /var/log/nginx/nsfw-analyzer-frontend-access.log

# Nginx error logs
tail -f /var/log/nginx/nsfw-analyzer-frontend-error.log
```

### 3. Security Updates
```bash
# Update dependencies
npm audit
npm audit fix

# Update Node.js version as needed
```

## 📊 Monitoring

### 1. Basic Metrics
- Page load times
- API response times
- Error rates
- User engagement

### 2. Tools
- Google Analytics (optional)
- Browser DevTools
- Nginx logs
- Backend API logs

## 🚨 Security Considerations

1. **Content Security Policy**: Already configured in nginx
2. **HTTPS Only**: Enforce SSL/TLS
3. **Regular Updates**: Keep dependencies updated
4. **Input Validation**: Handled by React and backend
5. **Rate Limiting**: Configure in nginx if needed

## 📱 Mobile Responsiveness

The frontend is built with Tailwind CSS and is fully responsive:
- Mobile-first design
- Touch-friendly interface
- Optimized for various screen sizes
- Progressive Web App (PWA) ready 