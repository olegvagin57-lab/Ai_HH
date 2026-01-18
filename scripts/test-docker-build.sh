#!/bin/bash
# Test script for Docker build locally
# Usage: ./scripts/test-docker-build.sh

set -e

# Check if DOCKER_USERNAME is set
if [ -z "$DOCKER_USERNAME" ]; then
  echo "❌ Error: DOCKER_USERNAME environment variable is not set!"
  echo "Set it with: export DOCKER_USERNAME=your-username"
  exit 1
fi

if [ -z "$DOCKER_PASSWORD" ]; then
  echo "❌ Error: DOCKER_PASSWORD environment variable is not set!"
  echo "Set it with: export DOCKER_PASSWORD=your-password"
  exit 1
fi

echo "✅ Docker Hub credentials are configured"
echo "Username: $DOCKER_USERNAME"
echo "Username length: ${#DOCKER_USERNAME}"

# Test login
echo "Logging in to Docker Hub..."
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

# Test tag format
SHORT_SHA="test123"
BACKEND_TAG="${DOCKER_USERNAME}/hh-analyzer-backend:latest"
FRONTEND_TAG="${DOCKER_USERNAME}/hh-analyzer-frontend:latest"

echo ""
echo "Tags that will be used:"
echo "Backend: $BACKEND_TAG"
echo "Frontend: $FRONTEND_TAG"

# Validate tag format
if [[ ! "$BACKEND_TAG" =~ ^[a-z0-9._-]+/[a-z0-9._-]+:[a-z0-9._-]+$ ]]; then
  echo "❌ Error: Invalid tag format for backend: $BACKEND_TAG"
  echo "Tags must be lowercase and contain only: [a-z0-9._-]"
  exit 1
fi

if [[ ! "$FRONTEND_TAG" =~ ^[a-z0-9._-]+/[a-z0-9._-]+:[a-z0-9._-]+$ ]]; then
  echo "❌ Error: Invalid tag format for frontend: $FRONTEND_TAG"
  exit 1
fi

echo ""
echo "✅ All tag formats are valid!"
echo ""
echo "To test build locally, run:"
echo "  docker build -t $BACKEND_TAG ./backend"
echo "  docker build -t $FRONTEND_TAG ./frontend"
