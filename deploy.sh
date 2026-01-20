#!/bin/bash
set -e

IMAGE="ghcr.io/mahsa472/rag-runtime:latest"
CONTAINER_NAME="rag-app"

echo "🚀 Starting deployment..."

# Pull latest code if in git repo
# Handle uncommitted changes and merge conflicts
if [ -d .git ]; then
    echo "📥 Updating code from repository..."
    
    # Abort any in-progress merge to clear merge conflicts
    if [ -f .git/MERGE_HEAD ]; then
        echo "⚠️  Merge conflict detected, aborting merge..."
        git merge --abort 2>/dev/null || true
    fi
    
    # Reset any merge/rebase state
    git reset --hard HEAD 2>/dev/null || true
    
    # Clean up any uncommitted changes
    git clean -fd || true
    git reset --hard HEAD || true
    
    # Fetch latest from origin
    git fetch origin main || echo "Git fetch failed"
    
    # Reset to match origin/main exactly (clean state)
    git reset --hard origin/main || echo "Git reset failed"
    
    echo "✅ Code updated successfully"
else
    echo "⚠️  Not a git repo, skipping code update"
fi

# Pull latest Docker images

docker pull $IMAGE
docker pull prom/prometheus:latest
docker pull grafana/grafana:latest

# Stop old standalone container if exists
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

# Set environment variables
export OPENAI_API_KEY=${OPENAI_API_KEY}
export GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-admin}

# Create .env file for docker-compose
echo "GRAFANA_PASSWORD=${GRAFANA_PASSWORD}" > .env
if [ ! -z "$OPENAI_API_KEY" ]; then
    echo "OPENAI_API_KEY=${OPENAI_API_KEY}" >> .env
fi

# Deploy all services
docker-compose down
docker-compose up -d

# Wait a moment for services to start
sleep 5

echo "✅ Deployment complete!"
