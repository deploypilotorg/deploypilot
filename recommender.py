from collections import Counter
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder, StandardScaler

class DeploymentPredictor:
    def __init__(self, dataset_path):
        # Load the dataset
        self.df = pd.read_csv(dataset_path)

        # Preprocess data
        self.df = self.df.infer_objects(copy=False)
        self.df = self.df.replace({"Yes": 1, "No": 0})

        # Separate features and target
        self.X = self.df.drop(["repository", "deployment"], axis=1)
        self.y = self.df["deployment"]

        # Encode the target variable
        self.le = LabelEncoder()
        self.y_encoded = self.le.fit_transform(self.y)

        # Convert boolean strings to integers (if needed)
        self.X = self.X.astype(int)

        # Initialize and fit the scaler
        self.scaler = StandardScaler()
        self.X_scaled = self.scaler.fit_transform(self.X)

        # Calculate cosine similarity matrix
        self.similarity_matrix = cosine_similarity(self.X_scaled)

    def predict_deployment(self, repository_name, n_similar=5):
        """
        Predict the deployment type based on similar repositories

        Args:
            repository_name (str): Name of the repository to predict deployment for
            n_similar (int): Number of similar repositories to consider for prediction

        Returns:
            str: Predicted deployment type
        """
        # Find the index of the repository
        idx = self.df[self.df["repository"] == repository_name].index[0]

        # Get similarity scores for this repository
        similarity_scores = list(enumerate(self.similarity_matrix[idx]))

        # Sort repositories by similarity score
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

        # Get top N most similar repositories (excluding itself)
        similar_repos = similarity_scores[1 : n_similar + 1]

        # Get the deployment types of the similar repositories
        similar_deployments = [self.y.iloc[idx] for idx, _ in similar_repos]

        # Predict deployment type based on the most common deployment type among similar repositories
        deployment_prediction = Counter(similar_deployments).most_common(1)[0][0]

        return deployment_prediction


# Example usage
if __name__ == "__main__":
    predictor = DeploymentPredictor("dataset.csv")
    sample_repo = "excalidraw/excalidraw"  # Replace with actual repository
    predicted_deployment = predictor.predict_deployment(sample_repo, n_similar=5)

    print(f"\nPredicted deployment type for {sample_repo}: {predicted_deployment}")
