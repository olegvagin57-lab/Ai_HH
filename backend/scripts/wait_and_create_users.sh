#!/bin/bash
set -e

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
  if curl -f -s http://localhost:8000/api/v1/health/ready > /dev/null 2>&1; then
    echo "Backend is ready!"
    break
  fi
  attempt=$((attempt + 1))
  echo "Attempt $attempt/$max_attempts: Backend not ready yet, waiting..."
  sleep 2
done

if [ $attempt -eq $max_attempts ]; then
  echo "Error: Backend not ready after $max_attempts attempts"
  exit 1
fi

# Create test users
echo "Creating test users..."
python scripts/create_test_users.py

echo "Test users setup completed!"
