# DeployPilot Frontend

A Flask-based web interface for DeployPilot, a tool that uses AI to automate Git operations and repository deployments.

## Overview

This application serves as the frontend for DeployPilot, connecting to a backend API server that uses MCP (Model-Code-Process) architecture to perform Git operations and deploy repositories.

## Features

- Interactive chat interface to communicate with the AI agent
- Workspace information display
- Workspace reset functionality
- Session management for chat history
- Real-time status monitoring

## Requirements

- Python 3.6+
- Flask
- Requests
- Python-dotenv (optional for environment variable management)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/deploypilotorg/deploypilot.git
   cd deploypilot
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the backend API server first (not included in this repository):
   ```
   # The API server should be running on http://127.0.0.1:8000
   ```

2. Start the frontend server:
   ```
   python main.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:8080
   ```

## Architecture

- **Frontend (this repository)**: Flask web application serving HTML/CSS/JS
- **Backend API Server**: Handles the actual Git operations and deployments using MCP
- **Communication**: HTTP/JSON between frontend and backend

## API Endpoints

- `/` - Main interface
- `/query` - Send queries to the agent
- `/status` - Check API server status
- `/workspace_info` - Get information about the current workspace
- `/reset_workspace` - Reset the workspace
- `/clear_chat` - Clear chat history

## Development

This is currently configured as a development server. For production use, consider:

1. Using a production WSGI server
2. Setting a secure secret key
3. Configuring proper HTTPS

## Automatic Deployment

This project includes a GitHub Actions workflow that automatically deploys changes to your Digital Ocean droplet whenever code is pushed to the `main` branch.

### Setting up GitHub Secrets

For the deployment workflow to work, you need to set up the following secrets in your GitHub repository:

1. Go to your GitHub repository > Settings > Secrets and variables > Actions
2. Add the following secrets:
   - `DROPLET_IP`: The IP address of your Digital Ocean droplet
   - `DROPLET_USERNAME`: The username to SSH into your droplet (usually 'root')
   - `SSH_PRIVATE_KEY`: Your private SSH key to access the droplet
   - `PROJECT_PATH`: The absolute path to your project directory on the droplet

### How It Works

1. When you push to the `main` branch, the GitHub Actions workflow triggers
2. It connects to your Digital Ocean droplet via SSH
3. It navigates to your project directory and pulls the latest changes
4. Optionally, it can restart any services if configured

If you need to restart a service (like a systemd service), uncomment and modify the service restart line in `.github/workflows/deploy.yml`.

