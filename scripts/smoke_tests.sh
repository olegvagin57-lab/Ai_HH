#!/bin/bash
# Smoke tests for production deployment
# These tests verify that the application is running correctly after deployment

set -e

BASE_URL="${1:-http://localhost:8000}"
MAX_RETRIES=30
RETRY_INTERVAL=2

echo "Running smoke tests against: $BASE_URL"

# Wait for service to be ready
echo "Waiting for service to be ready..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -f -s "$BASE_URL/api/v1/health/live" > /dev/null; then
        echo "Service is live!"
        break
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        echo "Service failed to become ready after $MAX_RETRIES attempts"
        exit 1
    fi
    echo "Attempt $i/$MAX_RETRIES: Service not ready, waiting..."
    sleep $RETRY_INTERVAL
done

# Health check
echo "Testing health endpoint..."
if ! curl -f -s "$BASE_URL/api/v1/health" > /dev/null; then
    echo "Health check failed!"
    exit 1
fi
echo "✓ Health check passed"

# Readiness check
echo "Testing readiness endpoint..."
if ! curl -f -s "$BASE_URL/api/v1/health/ready" > /dev/null; then
    echo "Readiness check failed!"
    exit 1
fi
echo "✓ Readiness check passed"

# Liveness check
echo "Testing liveness endpoint..."
if ! curl -f -s "$BASE_URL/api/v1/health/live" > /dev/null; then
    echo "Liveness check failed!"
    exit 1
fi
echo "✓ Liveness check passed"

# Metrics endpoint
echo "Testing metrics endpoint..."
if ! curl -f -s "$BASE_URL/metrics" > /dev/null; then
    echo "Metrics endpoint check failed!"
    exit 1
fi
echo "✓ Metrics endpoint accessible"

# API root endpoint
echo "Testing API root endpoint..."
RESPONSE=$(curl -s "$BASE_URL/")
if ! echo "$RESPONSE" | grep -q "HH Resume Analyzer"; then
    echo "API root endpoint check failed!"
    exit 1
fi
echo "✓ API root endpoint working"

echo ""
echo "All smoke tests passed! ✓"
