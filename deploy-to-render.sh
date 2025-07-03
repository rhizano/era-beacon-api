#!/bin/bash

echo "🚀 Preparing BLE Beacon API for Render.com deployment..."

# Make scripts executable
chmod +x build.sh start.sh

# Generate a secret key
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

echo "✅ Project prepared for Render.com!"
echo ""
echo "📋 Next Steps:"
echo "1. Push your code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Deploy to Render'"
echo "   git push origin main"
echo ""
echo "2. Go to https://render.com and create a new Web Service"
echo "3. Connect your GitHub repository"
echo "4. Use these settings:"
echo "   - Build Command: ./build.sh"
echo "   - Start Command: ./start.sh"
echo "   - Plan: Free"
echo ""
echo "5. Create a PostgreSQL database service"
echo ""
echo "6. Set these environment variables in Render:"
echo "   DATABASE_URL=<copy from your PostgreSQL service>"
echo "   SECRET_KEY=$SECRET_KEY"
echo "   ALGORITHM=HS256"
echo "   ACCESS_TOKEN_EXPIRE_MINUTES=30"
echo "   API_V1_STR=/v1"
echo "   PROJECT_NAME=BLE Beacon Presence Tracking API"
echo "   DEBUG=false"
echo ""
echo "📖 For detailed instructions, see: deployment/RENDER_DEPLOYMENT.md"
