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

## 🧪 Testing

### 1. Run Tests
```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage
```

### 2. Test Cases
The test suite includes:
- File upload handling
- Drag and drop functionality
- API integration
- Error handling
- Multiple category display
- Severity level visualization

### 3. Manual Testing Checklist
- [ ] File upload works with various video formats
- [ ] Drag and drop interface is responsive
- [ ] Loading states display correctly
- [ ] Error messages are clear and helpful
- [ ] Results display all categories correctly
- [ ] Severity levels are color-coded appropriately
- [ ] Mobile responsiveness works
- [ ] Browser compatibility (Chrome, Firefox, Safari, Edge)

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

## 🎨 UI Features

### 1. Content Analysis Display
- Status indicator (Safe/NSFW)
- Multiple category badges
- Severity level with color coding
- Analysis method used
- Detailed description

### 2. User Interface
- Drag and drop file upload
- File type validation
- Progress indicators
- Error handling
- Responsive design
- Mobile-friendly interface

### 3. Color Coding
- Safe: Green
- Suggestive: Blue
- Mature: Yellow
- Explicit: Orange
- Extreme: Red
- Illegal: Dark Red

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