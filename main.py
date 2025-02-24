"""
Main Streamlit application file
"""

from urllib.parse import urlparse

import requests
import streamlit as st
from dotenv import load_dotenv
from scraper import GitIngestScraper  # Import the scraper
from feature_analyzer import FeatureAnalyzer  # Import the FeatureAnalyzer
from recommender import DeploymentPredictor  # Import the DeploymentPredictor

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="GitHub Repository Analyzer", page_icon="🔍", layout="wide"
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

                # Display predicted deployment type at the top
                st.subheader("🔮 Predicted Deployment Type")
                st.write(f"The predicted deployment type for this repository is: **{predicted_deployment}**")

                # Create an expander for the rest of the information
                with st.expander("View Repository and Analysis Information"):
                    # Create two columns
                    col1, col2 = st.columns(2)

                    # Repository Information
                    with col1:
                        st.subheader("📊 Repository Information")
                        st.write(f"**Directory Structure:** {repo_data['directory_structure']}")
                        st.write(f"**Code Content:** {repo_data['textarea_content']}")

                    # Analysis Results
                    with col2:
                        st.subheader("🔍 Analysis Results")
                        st.write("### Infrastructure Features")
                        for feature, present in directory_analysis.items():
                            status = "✓" if present else "✗"
                            st.write(f"{feature.replace('_', ' ').title()}: {status}")

                        st.write("### Code Features")
                        for feature, data in code_analysis.items():
                            status = "✓" if data["present"] else "✗"
                            st.write(f"{feature.replace('_', ' ').title()}: {status}")
                            if data["present"]:
                                st.write(f"Details: {data['details']}")
                                if data.get("improvements"):
                                    st.write(f"Suggested Improvements: {data['improvements']}")

            else:
                st.error("Failed to fetch repository data")
    else:
        st.error("Please enter a valid GitHub repository URL")
