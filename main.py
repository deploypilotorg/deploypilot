"""
Main Streamlit application file with updated diagram rendering
"""

from urllib.parse import urlparse
import os
import base64
import subprocess
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from feature_analyzer import FeatureAnalyzer
from recommender import DeploymentPredictor
from scraper import GitIngestScraper
from diagram_generator import DiagramGenerator

# AWS Service Mappings
AWS_SERVICE_MAPPINGS = {
    'database': {
        'service': 'Amazon RDS or Amazon DynamoDB',
        'description': 'Managed relational or NoSQL database service'
    },
    'storage': {
        'service': 'Amazon S3',
        'description': 'Object storage for files and static assets'
    },
    'caching': {
        'service': 'Amazon ElastiCache',
        'description': 'In-memory caching for performance optimization'
    },
    'authentication': {
        'service': 'Amazon Cognito',
        'description': 'User authentication and authorization'
    },
    'realtime_events': {
        'service': 'Amazon EventBridge or AWS AppSync',
        'description': 'Real-time event processing and WebSocket support'
    },
    'message_queues': {
        'service': 'Amazon SQS',
        'description': 'Managed message queuing service'
    },
    'background_jobs': {
        'service': 'AWS Lambda with EventBridge',
        'description': 'Serverless functions for background processing'
    },
    'high_availability': {
        'service': 'AWS Auto Scaling with ELB',
        'description': 'High availability and load balancing'
    },
    'uses_containerization': {
        'service': 'Amazon ECS or EKS',
        'description': 'Container orchestration service'
    }
}

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="DeployPilot", page_icon="🚀", layout="wide"
)


def extract_repo_info(github_url):
    """Extract owner and repo name from GitHub URL"""
    path_parts = urlparse(github_url).path.strip("/").split("/")
    if len(path_parts) >= 2:
        return path_parts[0], path_parts[1]
    return None, None


def get_repo_data(owner, repo):
    """Fetch repository data using GitIngestScraper"""
    scraper = GitIngestScraper(f"{owner}/{repo}")
    return scraper.scrape()  # Use the scraper to get data


def render_mermaid_to_image(mermaid_code, output_path='diagram.png'):
    """
    Renders a Mermaid diagram to an image file using mmdc (mermaid-cli)
    
    Args:
        mermaid_code (str): The Mermaid diagram code
        output_path (str): Path to save the generated image
        
    Returns:
        str: Path to the generated image or None if failed
    """
    try:
        # Check if mmdc is installed
        result = subprocess.run(['which', 'mmdc'], capture_output=True, text=True)
        if not result.stdout:
            st.warning("Mermaid CLI (mmdc) is not installed. Installing it requires Node.js and npm.")
            st.info("Install with: npm install -g @mermaid-js/mermaid-cli")
            st.info("Using Streamlit's built-in Mermaid rendering instead.")
            return None
        
        # Create temp directory if it doesn't exist
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Create input file with Mermaid code
        input_file = temp_dir / "diagram.mmd"
        with open(input_file, "w") as f:
            f.write(mermaid_code)
        
        # Full path for output
        output_file = temp_dir / output_path
        
        # Run mmdc command to generate the PNG
        subprocess.run([
            'mmdc',
            '-i', str(input_file),
            '-o', str(output_file),
            '-b', 'transparent'
        ], check=True)
        
        return str(output_file)
    except subprocess.CalledProcessError as e:
        st.error(f"Error executing Mermaid CLI: {e}")
        return None
    except Exception as e:
        st.error(f"Error rendering Mermaid diagram: {str(e)}")
        return None


def render_mermaid_with_puppeteer(mermaid_code, output_path='diagram.png'):
    """
    Alternative Mermaid renderer using puppeteer directly via a temporary script
    This is a fallback in case mmdc is not installed
    
    Args:
        mermaid_code (str): The Mermaid diagram code
        output_path (str): Path to save the generated image
        
    Returns:
        str: Path to the generated image or None if failed
    """
    try:
        # Create temp directory if it doesn't exist
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Full path for output
        output_file = temp_dir / output_path
        
        # Create a simple HTML file with the Mermaid diagram
        html_file = temp_dir / "diagram.html"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>
                mermaid.initialize({{ startOnLoad: true }});
            </script>
        </head>
        <body>
            <div class="mermaid">
                {mermaid_code}
            </div>
        </body>
        </html>
        """
        
        with open(html_file, "w") as f:
            f.write(html_content)
        
        # Create a simple message to guide the user
        st.info(f"""
        Mermaid CLI not detected. You can view the diagram in your browser:
        1. Open the file: {html_file}
        2. Or use this Mermaid code with an online editor: https://mermaid.live
        """)
        
        # Return None to indicate image wasn't created
        return None
    except Exception as e:
        st.error(f"Error creating HTML file: {str(e)}")
        return None


def display_image(image_path):
    """Display an image in Streamlit from a file path"""
    if not image_path or not os.path.exists(image_path):
        st.error(f"Image file not found or not generated: {image_path}")
        return False
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        encoded_image = base64.b64encode(image_bytes).decode()
        
    st.markdown(
        f'<img src="data:image/png;base64,{encoded_image}" alt="Architecture Diagram" width="100%">',
        unsafe_allow_html=True
    )
    return True


# Title and description
st.title("🚀 DeployPilot")
st.markdown("Enter a GitHub repository URL to get a suggested architecture")

# GitHub token input (optional)
github_token = st.text_input(
    "GitHub Token (optional)",
    type="password",
    help="Enter your GitHub token to increase API rate limits",
)

# OpenAI API key input (for diagram generation)
openai_api_key = st.text_input(
    "OpenAI API Key",
    type="password",
    help="Enter your OpenAI API key for diagram generation",
)

# Repository URL input
raw_repo_url = st.text_input(
    "GitHub Repository URL", placeholder="owner/repo"
)

if raw_repo_url:
    owner, repo = extract_repo_info(raw_repo_url)
    if owner and repo:
        # Create placeholder for status messages
        status_container = st.empty()
        
        # Stage 1: Fetching repository
        status_container.markdown("🔄 Fetching repository data...")
        repo_data = get_repo_data(owner, repo)
        status_container.markdown("✅ Repository data fetched")
        
        if repo_data:
            # Stage 2: Analyzing structure
            status_container.markdown("✅ Repository data fetched\n\n🔄 Analyzing directory structure...")
            analyzer = FeatureAnalyzer()
            directory_analysis = analyzer.analyze_directory_structure(repo_data['directory_structure'])
            status_container.markdown("✅ Repository data fetched\n\n✅ Directory structure analyzed\n\n🔄 Analyzing code patterns...")
            
            # Stage 3: Analyzing code
            code_analysis = analyzer.analyze_with_llm(repo_data['textarea_content'])
            status_container.markdown("✅ Repository data fetched\n\n✅ Directory structure analyzed\n\n✅ Code patterns analyzed\n\n🔄 Generating deployment recommendations...")

            # Combine results into a single dictionary with 1s and 0s
            combined_results = {}

            # Unpack infrastructure analysis
            for feature, present in directory_analysis.items():
                combined_results[feature] = 1 if present else 0

            # Unpack code analysis
            for feature, data in code_analysis.items():
                combined_results[feature] = 1 if data["present"] else 0

            # Create an instance of DeploymentPredictor
            predictor = DeploymentPredictor("dataset.csv")

            # Convert combined_results into a feature vector
            feature_vector = list(combined_results.values())
                
            # Predict deployment type using the feature vector
            predicted_deployment = predictor.predict_from_vector(feature_vector)

            # Clear the status messages
            status_container.empty()
                
            # Display predicted deployment type at the top with a card-like container
            st.markdown("""
                <style>
                .deployment-card {
                    padding: 2rem;
                    border-radius: 10px;
                    border: 2px solid #e9ecef;
                    margin-bottom: 2rem;
                }
                .aws-service-card {
                    padding: 1rem;
                    border-radius: 8px;
                    border: 1px solid #dee2e6;
                    margin: 0.5rem 0;
                }
                </style>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div class='deployment-card'>
                    <h2>🔮 Deployment Recommendation</h2>
                    <h3 style='color: #0066cc;'>""" + predicted_deployment + """</h3>
                </div>
            """, unsafe_allow_html=True)

            # If AWS is recommended, show relevant services
            if predicted_deployment == "AWS":
                st.subheader("📦 Recommended AWS Services")
                    
                # Create three columns for AWS services
                cols = st.columns(3)
                col_idx = 0
                
                # Keep track of recommended services for diagram generation
                recommended_services = []
                    
                for feature, present in combined_results.items():
                    if present and feature in AWS_SERVICE_MAPPINGS:
                        service_info = AWS_SERVICE_MAPPINGS[feature]
                        recommended_services.append({
                            "feature": feature,
                            "service": service_info['service'],
                            "description": service_info['description']
                        })
                        with cols[col_idx % 3]:
                            st.markdown(f"""
                                <div class='aws-service-card'>
                                    <h4>{service_info['service']}</h4>
                                    <p>{service_info['description']}</p>
                                </div>
                            """, unsafe_allow_html=True)
                            col_idx += 1
                
                # Generate architecture diagram if OpenAI API key is provided
                if openai_api_key:
                    try:
                        # Set OpenAI API key in environment for the diagram generator
                        os.environ["OPENAI_API_KEY"] = openai_api_key
                        
                        # Create diagram generator instance
                        diagram_generator = DiagramGenerator()
                        
                        # Create structured input for diagram generation
                        services_info = "\n".join([f"- {s['service']}: {s['description']}" for s in recommended_services])
                        project_info = f"""
                        Repository: {owner}/{repo}
                        Recommended Deployment: AWS
                        Recommended Services:
                        {services_info}
                        
                        Directory Structure:
                        {repo_data['directory_structure']}
                        """
                        
                        # Generate diagram
                        st.subheader("📊 Architecture Diagram")
                        with st.spinner("Generating architecture diagram..."):
                            diagram_code = diagram_generator.generate_architecture_diagram(f"{owner}/{repo}", project_info)
                            
                            # Extract the mermaid code from the response
                            if "```mermaid" in diagram_code:
                                diagram_code = diagram_code.split("```mermaid")[1].split("```")[0].strip()
                            elif "```" in diagram_code:
                                diagram_code = diagram_code.split("```")[1].strip()
                            
                            # Display the raw Mermaid code in a collapsible section
                            with st.expander("View Mermaid Code"):
                                st.code(diagram_code, language="mermaid")
                            
                            # First try native Streamlit Mermaid rendering
                            st.write("### Rendered Diagram")
                            st.markdown(f"```mermaid\n{diagram_code}\n```")
                            
                            # Try to render the diagram as an image using mmdc
                            with st.spinner("Rendering diagram image (if Mermaid CLI is available)..."):
                                diagram_image_path = render_mermaid_to_image(diagram_code, f"{owner}_{repo}_diagram.png")
                                
                                # If mmdc is available, display the image
                                if diagram_image_path:
                                    st.write("### Exported Diagram Image")
                                    if display_image(diagram_image_path):
                                        # Add a download button for the diagram
                                        with open(diagram_image_path, "rb") as file:
                                            btn = st.download_button(
                                                label="Download Diagram",
                                                data=file,
                                                file_name=f"{owner}_{repo}_architecture.png",
                                                mime="image/png"
                                            )
                                # If mmdc is not available, create a simple HTML file
                                else:
                                    render_mermaid_with_puppeteer(diagram_code, f"{owner}_{repo}_diagram.png")
                    except Exception as e:
                        st.error(f"Error generating diagram: {str(e)}")
                else:
                    st.info("Enter an OpenAI API key to generate an architecture diagram.")

                # Create tabs for different sections of information
                tab1, tab2 = st.tabs(["📊 Analysis Results", "📁 Repository Details"])
                
                with tab1:
                    # Analysis Results in a more organized format
                    st.markdown("""
                        <style>
                        .feature-present { color: #28a745; }
                        .feature-absent { color: #dc3545; }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    infra_col, code_col = st.columns(2)
                    
                    with infra_col:
                        st.markdown("### 🏗️ Infrastructure Features")
                        for feature, present in directory_analysis.items():
                            status = "✓" if present else "✗"
                            color_class = "feature-present" if present else "feature-absent"
                            st.markdown(f"<span class='{color_class}'>{status}</span> {feature.replace('_', ' ').title()}", unsafe_allow_html=True)
                    with code_col:
                        st.markdown("### 💻 Code Features")
                        for feature, data in code_analysis.items():
                            status = "✓" if data["present"] else "✗"
                            color_class = "feature-present" if data["present"] else "feature-absent"
                            st.markdown(f"<span class='{color_class}'>{status}</span> {feature.replace('_', ' ').title()}", unsafe_allow_html=True)
                            if data["present"]:
                                with st.expander("View Details"):
                                    st.write(f"**Details:** {data['details']}")
                                    if data.get("improvements"):
                                        st.write(f"**Suggested Improvements:** {data['improvements']}")

                with tab2:
                    st.subheader("📁 Repository Structure")
                    st.write(repo_data['directory_structure'])
                    st.subheader("📝 Code Content")
                    with st.expander("View Code Content"):
                        st.code(repo_data['textarea_content'])

            else:
                st.error("Failed to fetch repository data")
    else:
        st.error("Please enter a valid GitHub repository URL")
