#!/bin/bash
# Build script for frontend

set -e

echo "Building React frontend..."

cd frontend

# Install dependencies
npm ci

# Build for production
npm run build

echo "Frontend build complete! Output in frontend/dist/"

