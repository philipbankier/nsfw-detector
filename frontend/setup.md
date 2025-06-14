# Frontend Setup Guide

## Project Structure
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── App.js           (copy NSFWVideoAnalyzer component here)
│   ├── index.js
│   └── index.css
├── package.json
├── tailwind.config.js
└── .env
```

## Quick Setup

### 1. Create React App Structure
```bash
# Create frontend directory
mkdir -p nsfw-analyzer-frontend/src nsfw-analyzer-frontend/public

cd nsfw-analyzer-frontend
```

### 2. Copy Configuration Files
Copy these files to the frontend directory:
- `package.json`
- `tailwind.config.js`

### 3. Create index.html
```bash
cat > public/index.html << 'EOL'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="NSFW Video Analyzer" />
    <title>NSFW Video Analyzer</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOL
```

### 4. Create index.js
```bash
cat > src/index.js << 'EOL'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOL
```

### 5. Create index.css
```bash
cat > src/index.css << 'EOL'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOL
```

### 6. Create App.js
Copy the NSFWVideoAnalyzer component from the artifact into `src/App.js` and wrap it:
```javascript
import React from 'react';
// ... paste the NSFWVideoAnalyzer component here ...

function App() {
  return <NSFWVideoAnalyzer />;
}

export default App;
```

### 7. Set Environment Variable
```bash
# Create .env file with your backend URL
echo "REACT_APP_API_URL=https://api.yourdomain.com" > .env
```

### 8. Install Dependencies
```bash
npm install
```

### 9. Build for Production
```bash
npm run build
```

## Deploy to Digital Ocean

### 1. Copy Build Files
```bash
# From your local machine
scp -r build/* user@your-droplet-ip:/var/www/nsfw-analyzer/
```

### 2. Configure Nginx (on droplet)
```bash
sudo nano /etc/nginx/sites-available/nsfw-analyzer-frontend
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/nsfw-analyzer;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # React Router support
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

### 3. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/nsfw-analyzer-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Add SSL (Optional)
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Development

### Run Development Server
```bash
npm start
# App will be available at http://localhost:3000
```

### Update Backend URL for Development
```bash
# In .env
REACT_APP_API_URL=http://localhost:8005
```

## Troubleshooting

### CORS Issues
Make sure your backend has the correct CORS settings for your frontend domain.

### Build Errors
1. Clear node_modules: `rm -rf node_modules package-lock.json`
2. Reinstall: `npm install`
3. Try building: `npm run build`

### Styling Issues
Ensure Tailwind CSS is properly configured and imported in index.css.