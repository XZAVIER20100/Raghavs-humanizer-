#!/usr/bin/env bash
# Exit on error
set -o errexit

# Build the frontend
cd frontend
npm install
npm run build
cd ..
