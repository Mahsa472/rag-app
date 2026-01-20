#!/bin/bash
set -e

IMAGE="ghcr.io/mahsa472/rag-runtime:latest"
CONTAINER_NAME="rag-app"

echo "🚀 Starting deployment..."

# Pull latest code if in git repo
# Handle uncommitted changes by stashing them first
if [ -d .git ]; then
    # Check if there are uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        git stash save "Auto-stash before deployment $(date +%Y%m%d-%H%M%S)"
    fi
    # Pull latest code
    git fetch origin main || echo "Git fetch failed"
    git reset --hard origin/main || git pull origin main || echo "Git pull failed"
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



# Deploy all services
docker-compose down
docker-compose up -d

# Wait a moment for services to start
sleep 5

echo "✅ Deployment complete!"
