# DeployPilot 🚀
DeployPilot is a tool that analyzes GitHub repositories and provides deployment recommendations based on the codebase's features and infrastructure patterns. It uses machine learning to suggest appropriate deployment platforms and AWS services.
## Features

- Analyzes repository structure and code patterns  


- Provides deployment recommendations (e.g., AWS, Heroku, etc.)  


- Suggests relevant AWS services based on detected features  


- Real-time code analysis using OpenAI's GPT models  


- Web interface built with Streamlit  
## Installation

1. Clone the repository:

   ```bash


   git clone https://github.com/yourusername/deploypilot.git


   cd deploypilot


   ```
2. Create a virtual environment:

   ```bash


   python -m venv venv


   source venv/bin/activate  # On Windows: venv\Scripts\activate


   ```
3. Install dependencies:


   ```bash


   pip install -r requirements.txt


   ```
## Setting Up the API Key

Instead of storing your OpenAI API key in a `.env` file, it's recommended to set it as an environment variable for better security.

### For Linux/macOS:

```bash


export OPENAI_API_KEY=your_openai_api_key_here


```

### For Windows (Command Prompt):

```cmd


set OPENAI_API_KEY=your_openai_api_key_here


```

To make this setting persistent, add the `export` or `set` command to your shell profile (`.bashrc`, `.zshrc`, or Windows environment variables).
## Usage
1. Start the Streamlit application:


   ```bash


   streamlit run main.py


   ```

2. Open your browser and navigate to the provided local URL (typically http://localhost:8501)

3. Enter a GitHub repository URL in the format: `https://github.com/owner/repo`

4. (Optional) Enter your GitHub token to increase API rate limits

5. Wait for the analysis to complete and view the recommendations

## How It Works

1. **Repository Scraping**: Uses Selenium to scrape repository data from GitHub (see `scraper.py`)


2. **Feature Analysis**: Analyzes the codebase for various features using:


   - Directory structure analysis (see `feature_analyzer.py`)


   - Code pattern analysis using OpenAI's GPT model (see `feature_analyzer.py`)


3. **Deployment Prediction**: Uses machine learning to predict the best deployment platform based on similar repositories (see `recommender.py`)


4. **AWS Service Recommendations**: Maps detected features to relevant AWS services (see `main.py`)
## Features Analyzed

| **Infrastructure Features**        | **Code Features**                    |
|------------------------------------|--------------------------------------|
| Deployment status                  | Authentication                       |
| Frontend presence                  | Real-time events                     |
| CI/CD pipelines                    | Storage implementation               |
| Multiple environments               | Caching mechanisms                   |
| Containerization                    | AI/ML implementations                |
| Infrastructure as Code              | Database usage                       |
| High availability setup             | Architecture patterns (Microservices/Monolithic) |
|                                    | API endpoints                        |
|                                    | Message queues                       |
|                                    | Background jobs                      |
|                                    | Sensitive data handling              |
|                                    | External API dependencies            |

# DeployPilot 🚀

DeployPilot is a tool that analyzes GitHub repositories and provides deployment recommendations based on the codebase's features and infrastructure patterns. It uses machine learning to suggest appropriate deployment platforms and AWS services.

## Features

- Analyzes repository structure and code patterns  


- Provides deployment recommendations (e.g., AWS, Heroku, etc.)  


- Suggests relevant AWS services based on detected features  


- Real-time code analysis using OpenAI's GPT models  


- Web interface built with Streamlit  

## Installation

1. Clone the repository:

   ```bash


   git clone https://github.com/yourusername/deploypilot.git


   cd deploypilot


   ```

2. Create a virtual environment:

   ```bash


   python -m venv venv


   source venv/bin/activate  # On Windows: venv\Scripts\activate


   ```
3. Install dependencies:

   ```bash


   pip install -r requirements.txt


   ```
## Setting Up the API Key
Instead of storing your OpenAI API key in a `.env` file, it's recommended to set it as an environment variable for better security.

### For Linux/macOS:

```bash


export OPENAI_API_KEY=your_openai_api_key_here


```

### For Windows (Command Prompt):

```cmd


set OPENAI_API_KEY=your_openai_api_key_here


```
To make this setting persistent, add the `export` or `set` command to your shell profile (`.bashrc`, `.zshrc`, or Windows environment variables).

## Usage

1. Start the Streamlit application:


   ```bash


   streamlit run main.py


   ```


2. Open your browser and navigate to the provided local URL (typically http://localhost:8501)


3. Enter a GitHub repository URL in the format: `https://github.com/owner/repo`


4. (Optional) Enter your GitHub token to increase API rate limits


5. Wait for the analysis to complete and view the recommendations

## How It Works

1. **Repository Scraping**: Uses Selenium to scrape repository data from GitHub (see `scraper.py`)


2. **Feature Analysis**: Analyzes the codebase for various features using:


   - Directory structure analysis (see `feature_analyzer.py`)


   - Code pattern analysis using OpenAI's GPT model (see `feature_analyzer.py`)


3. **Deployment Prediction**: Uses machine learning to predict the best deployment platform based on similar repositories (see `recommender.py`)


4. **AWS Service Recommendations**: Maps detected features to relevant AWS services (see `main.py`)


## Features Analyzed

| **Infrastructure Features**        | **Code Features**                    |
|------------------------------------|--------------------------------------|
| Deployment status                  | Authentication                       |
| Frontend presence                  | Real-time events                     |
| CI/CD pipelines                    | Storage implementation               |
| Multiple environments               | Caching mechanisms                   |
| Containerization                    | AI/ML implementations                |
| Infrastructure as Code              | Database usage                       |
| High availability setup             | Architecture patterns (Microservices/Monolithic) |
|                                    | API endpoints                        |
|                                    | Message queues                       |
|                                    | Background jobs                      |
|                                    | Sensitive data handling              |
|                                    | External API dependencies            |
