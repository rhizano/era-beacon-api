#!/bin/bash

# Era Beacon Scheduler Installation and Setup Script

echo "Setting up Era Beacon Notification Scheduler..."

# Create virtual environment
echo "Creating Python virtual environment..."
python -m venv scheduler_env

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source scheduler_env/Scripts/activate
else
    # Linux/macOS
    source scheduler_env/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create systemd service file (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Creating systemd service file..."
    
    cat > era-beacon-scheduler.service << EOF
[Unit]
Description=Era Beacon API Notification Scheduler
After=network.target

[Service]
Type=simple
User=\$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/scheduler_env/bin
ExecStart=$(pwd)/scheduler_env/bin/python $(pwd)/scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "Systemd service file created: era-beacon-scheduler.service"
    echo "To install the service, run:"
    echo "  sudo cp era-beacon-scheduler.service /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable era-beacon-scheduler"
    echo "  sudo systemctl start era-beacon-scheduler"
fi

echo ""
echo "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit config.ini to configure your scheduler settings"
echo "2. Test the scheduler: python scheduler.py"
echo "3. For production, consider using a process manager like systemd or supervisor"
echo ""
echo "To activate the virtual environment manually:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "  scheduler_env\\Scripts\\activate"
else
    echo "  source scheduler_env/bin/activate"
fi
