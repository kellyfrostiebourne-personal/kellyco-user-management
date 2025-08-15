# Makefile for Python Application
# This provides common commands for development and deployment

.PHONY: help install test run clean lint format web-app cli-tool

# Default target
help:
	@echo "🐍 Python Application - Available Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install     Install dependencies"
	@echo "  venv        Create virtual environment"
	@echo ""
	@echo "Development:"
	@echo "  run         Run the main application"
	@echo "  web-app     Run the Flask web application"
	@echo "  cli-tool    Run the CLI tool"
	@echo "  test        Run tests"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with Black"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean       Clean up generated files"
	@echo "  requirements Update requirements.txt"
	@echo ""
	@echo "Examples:"
	@echo "  make install && make run"
	@echo "  make web-app"
	@echo "  make cli-tool create -t 'Test task' -p high"

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source venv/bin/activate"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Dependencies installed successfully!"

# Run the main application
run:
	@echo "Running main application..."
	python3 main.py

# Run the Flask web application
web-app:
	@echo "Installing Flask..."
	pip install flask
	@echo "Starting Flask web application..."
	python3 web_app.py

# Run the CLI tool
cli-tool:
	@echo "Running CLI tool..."
	python3 cli_tool.py --help

# Run tests
test:
	@echo "Installing pytest..."
	pip install pytest
	@echo "Running tests..."
	python3 -m pytest src/tests/ -v

# Run linting
lint:
	@echo "Installing flake8..."
	pip install flake8
	@echo "Running linting checks..."
	flake8 src/ --max-line-length=88 --ignore=E203,W503

# Format code
format:
	@echo "Installing Black..."
	pip install black
	@echo "Formatting code..."
	black src/ --line-length=88

# Clean up generated files
clean:
	@echo "Cleaning up generated files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name "*.db" -delete
	find . -type f -name "*.json" -delete
	@echo "Cleanup complete!"

# Update requirements.txt
requirements:
	@echo "Updating requirements.txt..."
	pip freeze > requirements.txt
	@echo "Requirements updated!"

# Development setup (install all dev tools)
dev-setup: install
	@echo "Installing development tools..."
	pip install black flake8 mypy pytest pytest-cov
	@echo "Development setup complete!"

# Quick start (create venv, install deps, and run)
quick-start: venv
	@echo "Activating virtual environment and installing dependencies..."
	@echo "Please run: source venv/bin/activate && make install && make run"
