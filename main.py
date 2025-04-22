from flask import Flask, render_template, request, jsonify, session
import requests
import time
import json
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger('flask_github_agent')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # For session handling
app.config['SERVER_NAME'] = None  # Allow any host

# API server URL
API_URL = os.environ.get('API_URL', "http://127.0.0.1:8000")
logger.info(f"Using API URL: {API_URL}")

@app.route('/')
def index():
    # Initialize session if needed
    if 'messages' not in session:
        session['messages'] = []
    
    # Get workspace info
    try:
        workspace_response = requests.get(f"{API_URL}/workspace_info")
        if workspace_response.status_code == 200:
            workspace_info = workspace_response.json()
        else:
            workspace_info = {"error": "Unable to fetch workspace info"}
    except requests.exceptions.ConnectionError:
        workspace_info = {"error": "API server is not running"}
    
    return render_template('index.html', messages=session['messages'], workspace_info=workspace_info)

@app.route('/query', methods=['POST'])
def query():
    # Get the query from the form
    user_query = request.form.get('query', '')
    logger.info(f"Received query: {user_query}")
    
    if not user_query:
        return jsonify({"error": "Query cannot be empty"}), 400
    
    # Add user message to history
    if 'messages' not in session:
        session['messages'] = []
    
    session['messages'].append({"role": "user", "content": user_query})
    
    try:
        # Send the query to the agent server
        logger.info(f"Sending query to API server: {user_query}")
        response = requests.post(
            f"{API_URL}/query",
            json={"text": user_query}
        )
        
        if response.status_code != 200:
            error_msg = f"Error: Server returned status code {response.status_code}"
            logger.error(error_msg)
            session['messages'].append({"role": "assistant", "content": error_msg})
            session.modified = True
            return jsonify({"status": "error", "message": error_msg})
        
        data = response.json()
        query_id = data.get("query_id")
        
        if not query_id:
            error_msg = "Error: Failed to get query ID from server"
            logger.error(error_msg)
            session['messages'].append({"role": "assistant", "content": error_msg})
            session.modified = True
            return jsonify({"status": "error", "message": error_msg})
        
        logger.info(f"Query sent successfully. ID: {query_id}")
        
        # Poll for results
        max_retries = 300  # Wait up to 5 minutes
        for retry_count in range(max_retries):
            logger.info(f"Polling for results (attempt {retry_count + 1}/{max_retries})...")
            result_response = requests.get(f"{API_URL}/result/{query_id}")
            
            if result_response.status_code != 200:
                error_msg = f"Error: Server returned status code {result_response.status_code} when fetching results"
                logger.error(error_msg)
                session['messages'].append({"role": "assistant", "content": error_msg})
                session.modified = True
                return jsonify({"status": "error", "message": error_msg})
            
            result_data = result_response.json()
            status = result_data.get("status")
            
            if status == "completed":
                result = result_data.get("result", "No result returned")
                logger.info(f"Query completed: {result[:100]}...")
                session['messages'].append({"role": "assistant", "content": result})
                session.modified = True
                return jsonify({"status": "success", "message": result})
            elif status == "error":
                error_msg = result_data.get("result", "An error occurred but no details were provided")
                logger.error(error_msg)
                session['messages'].append({"role": "assistant", "content": error_msg})
                session.modified = True
                return jsonify({"status": "error", "message": error_msg})
            elif status == "not_found":
                error_msg = "Error: Query not found on server"
                logger.error(error_msg)
                session['messages'].append({"role": "assistant", "content": error_msg})
                session.modified = True
                return jsonify({"status": "error", "message": error_msg})
            
            # Wait before polling again
            time.sleep(1)
        
        error_msg = "Error: Timed out waiting for response from agent"
        logger.error(error_msg)
        session['messages'].append({"role": "assistant", "content": error_msg})
        session.modified = True
        return jsonify({"status": "error", "message": error_msg})
    
    except requests.exceptions.ConnectionError:
        error_msg = "Error: Could not connect to the agent server. Make sure it's running at http://127.0.0.1:8000"
        logger.error(error_msg)
        session['messages'].append({"role": "assistant", "content": error_msg})
        session.modified = True
        return jsonify({"status": "error", "message": error_msg})
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg)
        session['messages'].append({"role": "assistant", "content": error_msg})
        session.modified = True
        return jsonify({"status": "error", "message": error_msg})

@app.route('/status')
def status():
    try:
        logger.info(f"Checking API status at {API_URL}/docs")
        response = requests.get(f"{API_URL}/docs", timeout=5)
        logger.info(f"Status response code: {response.status_code}")
        if response.status_code == 200:
            logger.info("API is online")
            return jsonify({"status": "online"})
        else:
            logger.warning(f"API returned error status: {response.status_code}")
            return jsonify({"status": "error", "code": response.status_code})
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error checking API status: {str(e)}")
        return jsonify({"status": "offline", "error": str(e)})
    except requests.exceptions.Timeout:
        logger.error("Timeout checking API status")
        return jsonify({"status": "timeout"})
    except Exception as e:
        logger.error(f"Unexpected error checking API status: {str(e)}")
        return jsonify({"status": "error", "error": str(e)})

@app.route('/workspace_info')
def workspace_info():
    try:
        logger.info(f"Fetching workspace info from {API_URL}/workspace_info")
        response = requests.get(f"{API_URL}/workspace_info", timeout=10)
        logger.info(f"Workspace info response status: {response.status_code}")
        
        if response.status_code == 200:
            # Log raw response for debugging
            raw_response = response.text
            logger.info(f"Raw workspace info response: {raw_response[:500]}...")
            
            try:
                data = response.json()
                logger.info("Successfully parsed workspace info JSON")
                return jsonify(data)
            except json.JSONDecodeError as e:
                error_msg = f"Error parsing workspace info JSON: {str(e)}"
                logger.error(error_msg)
                logger.error(f"Response content that failed to parse: {raw_response[:500]}...")
                return jsonify({"error": error_msg})
        else:
            error_msg = f"Server returned status code {response.status_code}"
            logger.error(error_msg)
            return jsonify({"error": error_msg})
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Could not connect to the agent server: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg})
    except requests.exceptions.Timeout:
        error_msg = "Request to API timed out"
        logger.error(error_msg)
        return jsonify({"error": error_msg})
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg})

@app.route('/reset_workspace', methods=['POST'])
def reset_workspace():
    try:
        logger.info(f"Resetting workspace via {API_URL}/reset_workspace")
        response = requests.post(f"{API_URL}/reset_workspace", timeout=30)
        logger.info(f"Reset workspace response status: {response.status_code}")
        
        if response.status_code == 200:
            # Log raw response for debugging
            raw_response = response.text
            logger.info(f"Raw reset workspace response: {raw_response[:500]}...")
            
            try:
                data = response.json()
                logger.info(f"Workspace reset: {data.get('message', '')}")
                return jsonify(data)
            except json.JSONDecodeError as e:
                error_msg = f"Error parsing reset workspace JSON response: {str(e)}"
                logger.error(error_msg)
                logger.error(f"Response content that failed to parse: {raw_response[:500]}...")
                return jsonify({"status": "error", "message": error_msg})
        else:
            error_msg = f"Error: Server returned status code {response.status_code}"
            logger.error(error_msg)
            return jsonify({"status": "error", "message": error_msg})
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Error: Could not connect to the agent server: {str(e)}"
        logger.error(error_msg)
        return jsonify({"status": "error", "message": error_msg})
    except requests.exceptions.Timeout:
        error_msg = "Error: Request to reset workspace timed out"
        logger.error(error_msg)
        return jsonify({"status": "error", "message": error_msg})
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg)
        return jsonify({"status": "error", "message": error_msg})

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    session['messages'] = []
    session.modified = True
    return jsonify({"status": "success"})

if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    logger.info("Starting Flask GitHub Agent UI...")
    # Use port 8080 instead of 5000, and bind to all interfaces
    app.run(debug=True, port=8080, host='0.0.0.0') 