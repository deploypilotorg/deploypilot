"""
Main Streamlit application file
"""

from urllib.parse import urlparse

import requests
import streamlit as st
from dotenv import load_dotenv
from scraper import GitIngestScraper  # Import the scraper

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
st.title("🔍 GitHub Repository Analyzer")
st.markdown("Enter a GitHub repository URL to analyze its details and metrics.")

# GitHub token input (optional)
github_token = st.text_input(
    "GitHub Token (optional)",
    type="password",
    help="Enter your GitHub token to increase API rate limits",
)

# Repository URL input
raw_repo_url = st.text_input(
    "GitHub Repository URL", placeholder="https://github.com/owner/repository"
)

if raw_repo_url:
    owner, repo = extract_repo_info(raw_repo_url)
    if owner and repo:
        with st.spinner("Fetching repository data..."):
            repo_data = get_repo_data(owner, repo)  # Update to use the scraper
            if repo_data:
                # Create two columns
                col1, col2 = st.columns(2)
                # Repository Information
                with col1:
                    st.subheader("📊 Repository Information")
                    st.write(f"**Directory Structure:** {repo_data['directory_structure']}")
                    st.write(f"**Code Content:** {repo_data['textarea_content']}")
                # Additional metrics can be added here if needed
            else:
                st.error("Failed to fetch repository data")
    else:
        st.error("Please enter a valid GitHub repository URL")
