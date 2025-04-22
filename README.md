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

