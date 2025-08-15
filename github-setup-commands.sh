#!/bin/bash
# GitHub Setup Commands for KellyCo User Management System
# Replace YOUR_GITHUB_URL with your actual repository URL

echo "🔗 Setting up GitHub remote and pushing code..."

# 1. Add your GitHub repository as remote origin
# Replace with your actual GitHub repository URL
git remote add origin YOUR_GITHUB_URL

# 2. Rename the main branch to 'main' (GitHub default)
git branch -M main

# 3. Push all code to GitHub
git push -u origin main

echo "✅ Code successfully pushed to GitHub!"
echo "🌐 Visit your repository at: YOUR_GITHUB_URL"

# Example URLs (replace with yours):
# git remote add origin https://github.com/kelly-fracis/kellyco-user-management.git
# or
# git remote add origin git@github.com:kelly-fracis/kellyco-user-management.git
