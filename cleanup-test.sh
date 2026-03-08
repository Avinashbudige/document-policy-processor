#!/bin/bash

# Cleanup script for local Lambda testing

echo "Stopping and removing test container..."
docker stop lambda-test 2>/dev/null || true
docker rm lambda-test 2>/dev/null || true

echo "Removing test image..."
docker rmi document-policy-processor:test 2>/dev/null || true

echo "Cleanup complete!"
