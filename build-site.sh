#!/usr/bin/env bash
# Rebuild the frontend and copy it into backend/static so the backend
# serves both the site and the API from one service.
set -e
cd "$(dirname "$0")"
cd frontend
npm install
npm run build
rm -rf ../backend/static
cp -r dist ../backend/static
echo "Done — backend/static updated. Restart the backend to pick it up."
