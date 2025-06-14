# Deployment Checklist

Complete checklist for deploying the NSFW Video Analyzer to production.

## 🔧 Pre-Deployment Setup

### Server Requirements
- [ ] Ubuntu 22.04+ server with minimum 2GB RAM
- [ ] Domain name configured (A records pointing to server)
- [ ] SSH access configured
- [ ] Firewall configured (ports 22, 80, 443 open)

### API Keys
- [ ] Google Gemini API key obtained
- [ ] Replicate API key obtained  
- [ ] Grok (x.ai) API key obtained
- [ ] All API keys tested and working

## 🚀 Backend Deployment

### System Dependencies
- [ ] Python 3.11+ installed
- [ ] FFmpeg installed and working (`ffmpeg -version`)
- [ ] Nginx installed
- [ ] Certbot installed (for SSL)

### Application Setup
- [ ] Backend files copied to `/opt/nsfw-analyzer/backend/`
- [ ] Virtual environment created and activated
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with real API keys
- [ ] File permissions set correctly

### Service Configuration
- [ ] Systemd service file copied to `/etc/systemd/system/`
- [ ] Service enabled (`sudo systemctl enable nsfw-analyzer`)
- [ ] Service started (`sudo systemctl start nsfw-analyzer`)
- [ ] Service status verified (`sudo systemctl status nsfw-analyzer`)

### Directory Setup
- [ ] Log directory created (`/var/log/nsfw-analyzer`)
- [ ] Temp directory created (`/tmp/nsfw-analyzer`)
- [ ] Proper ownership set (`www-data:www-data`)

### Nginx Backend Configuration
- [ ] Backend nginx config copied to `/etc/nginx/sites-available/`
- [ ] Symlink created in `/etc/nginx/sites-enabled/`
- [ ] Domain name updated in config
- [ ] Nginx configuration tested (`sudo nginx -t`)
- [ ] Nginx reloaded (`sudo systemctl reload nginx`)

## 🎨 Frontend Deployment

### Build Process
- [ ] Node.js 16+ installed locally
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Production API URL set in `.env`
- [ ] Production build created (`npm run build`)
- [ ] Build tested locally (optional)

### Server Setup
- [ ] Web directory created (`/var/www/nsfw-analyzer`)
- [ ] Build files copied to server
- [ ] File permissions set (`www-data:www-data`)

### Nginx Frontend Configuration
- [ ] Frontend nginx config copied to `/etc/nginx/sites-available/`
- [ ] Symlink created in `/etc/nginx/sites-enabled/`
- [ ] Domain names updated in config
- [ ] CSP header updated with correct API domain
- [ ] Nginx configuration tested (`sudo nginx -t`)
- [ ] Nginx reloaded (`sudo systemctl reload nginx`)

## 🔒 SSL/TLS Setup

### Certificate Installation
- [ ] Certbot installed
- [ ] SSL certificate obtained for backend domain
- [ ] SSL certificate obtained for frontend domain
- [ ] Auto-renewal tested (`sudo certbot renew --dry-run`)
- [ ] HTTP to HTTPS redirect working

### Security Headers
- [ ] Security headers configured in nginx
- [ ] Content Security Policy (CSP) configured
- [ ] HSTS headers enabled

## 🧪 Testing

### Backend Testing
- [ ] Health endpoint accessible (`curl https://api.yourdomain.com/health`)
- [ ] API keys status verified in health response
- [ ] Test video analysis working
- [ ] Error handling tested with invalid files
- [ ] Logs being written correctly

### Frontend Testing
- [ ] Website loads at `https://yourdomain.com`
- [ ] Upload interface functional
- [ ] Drag and drop working
- [ ] File validation working
- [ ] API integration working
- [ ] Results display correctly
- [ ] Error messages display properly

### Cross-Browser Testing
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### Mobile Testing
- [ ] Responsive design working
- [ ] Touch interface functional
- [ ] File upload working on mobile

## 📊 Monitoring Setup

### Log Monitoring
- [ ] Backend logs accessible (`/var/log/nsfw-analyzer/`)
- [ ] Nginx logs accessible (`/var/log/nginx/`)
- [ ] Log rotation configured
- [ ] Disk space monitoring for logs

### Service Monitoring
- [ ] Systemd service auto-restart configured
- [ ] Service status monitoring setup
- [ ] Resource usage monitoring (CPU, RAM, disk)

### Application Monitoring
- [ ] API response time monitoring
- [ ] Error rate monitoring
- [ ] Upload success rate tracking

## 🔐 Security Checklist

### Server Security
- [ ] SSH key-based authentication only
- [ ] Root login disabled
- [ ] Firewall configured (UFW or iptables)
- [ ] Fail2ban installed and configured
- [ ] Regular security updates enabled

### Application Security
- [ ] API keys stored securely (not in code)
- [ ] File upload limits configured
- [ ] Input validation working
- [ ] CORS properly configured
- [ ] Rate limiting considered

### SSL/TLS Security
- [ ] Strong SSL ciphers configured
- [ ] TLS 1.2+ only
- [ ] HSTS headers enabled
- [ ] Certificate auto-renewal working

## 🚀 Go-Live Checklist

### Final Verification
- [ ] All tests passing
- [ ] Performance acceptable
- [ ] Error handling working
- [ ] Monitoring in place
- [ ] Backup strategy defined

### Documentation
- [ ] API documentation accessible
- [ ] Deployment notes documented
- [ ] Troubleshooting guide available
- [ ] Contact information for support

### Communication
- [ ] Stakeholders notified of go-live
- [ ] Support team briefed
- [ ] Rollback plan documented

## 📋 Post-Deployment

### Immediate Actions (First 24 hours)
- [ ] Monitor logs for errors
- [ ] Check service stability
- [ ] Verify SSL certificates
- [ ] Test core functionality
- [ ] Monitor resource usage

### First Week
- [ ] Review performance metrics
- [ ] Check error rates
- [ ] Verify backup processes
- [ ] Update documentation as needed
- [ ] Gather user feedback

### Ongoing Maintenance
- [ ] Regular security updates
- [ ] Log rotation and cleanup
- [ ] Performance monitoring
- [ ] Capacity planning
- [ ] API key rotation schedule

## 🚨 Emergency Procedures

### Rollback Plan
- [ ] Previous version backup available
- [ ] Rollback procedure documented
- [ ] Database rollback plan (if applicable)
- [ ] DNS rollback procedure

### Incident Response
- [ ] Monitoring alerts configured
- [ ] Escalation procedures defined
- [ ] Emergency contacts list
- [ ] Status page setup (optional)

## 📞 Support Information

### Key Contacts
- [ ] System administrator contact
- [ ] Developer contact
- [ ] Domain/DNS provider contact
- [ ] Hosting provider contact

### Important URLs
- [ ] Frontend: `https://yourdomain.com`
- [ ] Backend API: `https://api.yourdomain.com`
- [ ] Health check: `https://api.yourdomain.com/health`

### Credentials
- [ ] Server SSH access documented
- [ ] API keys securely stored
- [ ] SSL certificate locations documented
- [ ] Service account credentials secured

---

## ✅ Deployment Complete

Once all items are checked:

1. **Announce go-live** to stakeholders
2. **Begin monitoring** for issues
3. **Document any deviations** from this checklist
4. **Schedule first maintenance window**
5. **Celebrate successful deployment!** 🎉

---

**Last Updated**: [Date]  
**Deployed By**: [Name]  
**Version**: [Version Number] 