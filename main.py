"""
Main Streamlit application file
"""

from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv
from scraper import GitIngestScraper
from feature_analyzer import FeatureAnalyzer
from recommender import DeploymentPredictor

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


# Title and description
st.title("🚀 DeployPilot")
st.markdown("Enter a GitHub repository URL to get a suggested architecture")

# GitHub token input (optional)
github_token = st.text_input(
    "GitHub Token (optional)",
    type="password",
    help="Enter your GitHub token to increase API rate limits",
)

# Repository URL input
raw_repo_url = st.text_input(
    "GitHub Repository URL", placeholder="owner/repo"
)

if raw_repo_url:
    owner, repo = extract_repo_info(raw_repo_url)
    if owner and repo:
        with st.spinner("Fetching repository data..."):
            repo_data = get_repo_data(owner, repo)  # Update to use the scraper
            if repo_data:
                # Create an instance of FeatureAnalyzer
                analyzer = FeatureAnalyzer()

                # Analyze the directory structure and code content
                directory_analysis = analyzer.analyze_directory_structure(repo_data['directory_structure'])
                code_analysis = analyzer.analyze_with_llm(repo_data['textarea_content'])

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
                    
                    for feature, present in combined_results.items():
                        if present and feature in AWS_SERVICE_MAPPINGS:
                            service_info = AWS_SERVICE_MAPPINGS[feature]
                            with cols[col_idx % 3]:
                                st.markdown(f"""
                                    <div class='aws-service-card'>
                                        <h4>{service_info['service']}</h4>
                                        <p>{service_info['description']}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                                col_idx += 1

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
                    st.json(repo_data['directory_structure'])
                    
                    st.subheader("📝 Code Content")
                    with st.expander("View Code Content"):
                        st.code(repo_data['textarea_content'])

            else:
                st.error("Failed to fetch repository data")
    else:
        st.error("Please enter a valid GitHub repository URL")
