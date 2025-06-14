#!/bin/bash
# NSFW Video Analyzer - Backend Setup Script

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/nsfw-analyzer"
BACKEND_DIR="$APP_DIR/backend"
SERVICE_NAME="nsfw-analyzer"
PYTHON_VERSION="python3.11"

echo -e "${GREEN}🚀 NSFW Video Analyzer - Backend Setup${NC}"
echo "======================================"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root!${NC}"
   exit 1
fi

# Step 1: Install system dependencies
echo -e "\n${YELLOW}📦 Installing system dependencies...${NC}"
sudo apt update
sudo apt install -y $PYTHON_VERSION ${PYTHON_VERSION}-venv python3-pip nginx ffmpeg

# Check ffmpeg installation
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}❌ FFmpeg installation failed${NC}"
    exit 1
fi

# Step 2: Create application directory
echo -e "\n${YELLOW}📁 Creating application directory...${NC}"
sudo mkdir -p $BACKEND_DIR
sudo chown -R $USER:$USER $APP_DIR

# Step 3: Setup Python environment
echo -e "\n${YELLOW}🐍 Setting up Python environment...${NC}"
cd $BACKEND_DIR

# Create virtual environment
$PYTHON_VERSION -m venv venv
source venv/bin/activate

# Copy files (assuming they're in current directory)
echo -e "\n${YELLOW}📄 Copying application files...${NC}"
cp main.py requirements.txt $BACKEND_DIR/ 2>/dev/null || {
    echo -e "${RED}❌ Could not find main.py and requirements.txt in current directory${NC}"
    echo "Please ensure these files are in the current directory and run again."
    exit 1
}

# Install Python dependencies
echo -e "\n${YELLOW}📚 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Create directories
echo -e "\n${YELLOW}📂 Creating required directories...${NC}"
sudo mkdir -p /var/log/nsfw-analyzer
sudo mkdir -p /tmp/nsfw-analyzer
sudo chown www-data:www-data /var/log/nsfw-analyzer
sudo chown www-data:www-data /tmp/nsfw-analyzer

# Step 5: Setup environment variables
echo -e "\n${YELLOW}🔑 Setting up environment variables...${NC}"
if [ -f .env ]; then
    echo -e "${GREEN}✅ .env file found${NC}"
else
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cat > .env << EOL
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
REPLICATE_API_KEY=your_replicate_api_key_here
GROK_API_KEY=your_grok_api_key_here
EOL
    echo -e "${RED}⚠️  Please edit .env file and add your API keys!${NC}"
fi

# Step 6: Setup systemd service
echo -e "\n${YELLOW}⚙️  Setting up systemd service...${NC}"

# Load environment variables for service
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create service file
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOL
[Unit]
Description=NSFW Video Analyzer API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=${BACKEND_DIR}
Environment="PATH=${BACKEND_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=${BACKEND_DIR}"
EnvironmentFile=${BACKEND_DIR}/.env
ExecStart=${BACKEND_DIR}/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8005 --workers 2

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=${SERVICE_NAME}

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/tmp/nsfw-analyzer /var/log/nsfw-analyzer

[Install]
WantedBy=multi-user.target
EOL

# Set permissions on .env file
sudo chown www-data:www-data $BACKEND_DIR/.env
sudo chmod 600 $BACKEND_DIR/.env

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}

echo -e "\n${YELLOW}🔧 Starting service...${NC}"
sudo systemctl start ${SERVICE_NAME}

# Wait a moment for service to start
sleep 3

# Check service status
if sudo systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✅ Service is running!${NC}"
else
    echo -e "${RED}❌ Service failed to start${NC}"
    echo "Check logs with: sudo journalctl -u ${SERVICE_NAME} -n 50"
    exit 1
fi

# Step 7: Test the API
echo -e "\n${YELLOW}🧪 Testing API...${NC}"
if curl -s http://localhost:8005/health > /dev/null; then
    echo -e "${GREEN}✅ API is responding!${NC}"
    
    # Show health status
    echo -e "\n${YELLOW}Health check results:${NC}"
    curl -s http://localhost:8005/health | python3 -m json.tool
else
    echo -e "${RED}❌ API is not responding${NC}"
    echo "Check logs with: sudo journalctl -u ${SERVICE_NAME} -f"
fi

# Final instructions
echo -e "\n${GREEN}✨ Backend setup complete!${NC}"
echo -e "\nNext steps:"
echo -e "1. ${YELLOW}Edit API keys:${NC} nano ${BACKEND_DIR}/.env"
echo -e "2. ${YELLOW}Restart service:${NC} sudo systemctl restart ${SERVICE_NAME}"
echo -e "3. ${YELLOW}Setup Nginx:${NC} Configure your nginx proxy"
echo -e "4. ${YELLOW}Test upload:${NC} python3 test_api.py sample_video.mp4"
echo -e "\nUseful commands:"
echo -e "- View logs: sudo journalctl -u ${SERVICE_NAME} -f"
echo -e "- Check status: sudo systemctl status ${SERVICE_NAME}"
echo -e "- Restart: sudo systemctl restart ${SERVICE_NAME}"