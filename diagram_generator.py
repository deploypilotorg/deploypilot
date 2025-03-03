import openai
import os
from dotenv import load_dotenv

class DiagramGenerator:
    def __init__(self):
        """
        Initializes the DiagramGenerator by loading API credentials
        and setting up the OpenAI client.
        """
        # Load environment variables from .env file
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

        self.client = openai.OpenAI(api_key=api_key)

        # Default configuration
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.7

    def generate_architecture_diagram(self, repo_name: str, project_structure: str) -> str:
        """
        Generates a Mermaid.js diagram representing the project architecture.

        Args:
            repo_name (str): The name of the repository.
            project_structure (str): A textual representation of the project structure.

        Returns:
            str: Mermaid.js formatted architecture diagram.
        """
        prompt = (
            f"""Analyze the following project structure for {repo_name} and generate a Mermaid.js architecture diagram 
            representing the system architecture, including key services, components, and their interactions.
            Ensure the output follows Mermaid.js syntax.
            
            Example:
            ```mermaid
            graph TD;
                A[Frontend] -->|API Call| B[Backend]
                B -->|Database Query| C[Database]
            ```
            Please refer to the actual names of the services instead of just frontend and backend if you can. 
            Project Structure:
            {project_structure}
            """
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in cloud architecture and visualization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )

            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Error generating architecture diagram: {str(e)}"
