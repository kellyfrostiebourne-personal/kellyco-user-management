#!/bin/bash
# Script to push KellyCo User Management System to GitHub
# Repository: https://github.com/kellyfrostiebourne-personal/kellyco-user-management

echo "🚀 Pushing KellyCo User Management System to GitHub..."

# Add the remote repository
git remote add origin https://github.com/kellyfrostiebourne-personal/kellyco-user-management.git

# Rename branch to main (GitHub's default)
git branch -M main

# Push to GitHub
git push -u origin main

echo "✅ Successfully pushed to GitHub!"
echo "🌐 Your repository: https://github.com/kellyfrostiebourne-personal/kellyco-user-management"

# Make the script executable
chmod +x push-to-github.sh
