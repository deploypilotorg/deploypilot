"""
Main Streamlit application file
"""

import os
from urllib.parse import urlparse

import requests
import streamlit as st
from dotenv import load_dotenv

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


def get_repo_data(owner, repo, token=None):
    """Fetch repository data from GitHub API"""
    headers = {"Authorization": f"token {token}"} if token else {}
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    user_url = f"https://api.github.com/users/{owner}"
    try:
        repo_response = requests.get(repo_url, headers=headers)
        user_response = requests.get(user_url, headers=headers)
        if repo_response.status_code == 200 and user_response.status_code == 200:
            return repo_response.json(), user_response.json()
        else:
            st.error("Error fetching data from GitHub API")
            return None, None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, None


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
repo_url = st.text_input(
    "GitHub Repository URL", placeholder="https://github.com/owner/repository"
)

if repo_url:
    owner, repo = extract_repo_info(repo_url)
    if owner and repo:
        with st.spinner("Fetching repository data..."):
            repo_data, user_data = get_repo_data(owner, repo, github_token)
            if repo_data and user_data:
                # Create two columns
                col1, col2 = st.columns(2)
                # Repository Information
                with col1:
                    st.subheader("📊 Repository Information")
                    st.write(f"**Name:** {repo_data['name']}")
                    st.write(f"**Description:** {repo_data['description']}")
                    st.write(f"**Stars:** {repo_data['stargazers_count']:,}")
                    st.write(f"**Forks:** {repo_data['forks_count']:,}")
                    st.write(f"**Open Issues:** {repo_data['open_issues_count']:,}")
                    st.write(f"**Language:** {repo_data['language']}")
                    st.write(f"**Created:** {repo_data['created_at'][:10]}")
                    st.write(f"**Last Updated:** {repo_data['updated_at'][:10]}")
                # Owner Information
                with col2:
                    st.subheader("👤 Owner Information")
                    st.image(user_data["avatar_url"], width=150)
                    st.write(f"**Username:** {user_data['login']}")
                    st.write(f"**Name:** {user_data.get('name', 'N/A')}")
                    st.write(f"**Followers:** {user_data['followers']:,}")
                    st.write(f"**Following:** {user_data['following']:,}")
                    st.write(f"**Public Repos:** {user_data['public_repos']:,}")
                    st.write(f"**Location:** {user_data.get('location', 'N/A')}")
                # Additional repository metrics
                st.subheader("📈 Repository Metrics")
                metrics_cols = st.columns(4)
                with metrics_cols[0]:
                    st.metric("Watch Count", repo_data["subscribers_count"])
                with metrics_cols[1]:
                    st.metric("Star Count", repo_data["stargazers_count"])
                with metrics_cols[2]:
                    st.metric("Fork Count", repo_data["forks_count"])
                with metrics_cols[3]:
                    st.metric("Open Issues", repo_data["open_issues_count"])
    else:
        st.error("Please enter a valid GitHub repository URL")
