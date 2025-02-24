import warnings
from collections import Counter

import numpy as np

warnings.simplefilter(action="ignore", category=FutureWarning)

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

    def predict_from_vector(self, feature_vector, n_similar=5):
        """
        Predict deployment type for a custom feature vector
        Args:
            feature_vector (list or np.array): Feature vector matching the training data features
            n_similar (int): Number of similar repositories to consider for prediction
        Returns:
            str: Predicted deployment type
        """
        # Validate input vector
        if len(feature_vector) != self.X.shape[1]:
            raise ValueError(
                f"Feature vector must have {self.X.shape[1]} features, got {len(feature_vector)}"
            )

        # Convert to numpy array and reshape
        feature_vector = np.array(feature_vector).reshape(1, -1)

        # Scale the input vector using the same scaler
        scaled_vector = self.scaler.transform(feature_vector)

        # Calculate similarity between input vector and all repositories
        similarities = cosine_similarity(scaled_vector, self.X_scaled)[0]

        # Get indices of most similar repositories
        similar_indices = np.argsort(similarities)[::-1][:n_similar]

        # Get deployment types of similar repositories
        similar_deployments = [self.y.iloc[idx] for idx in similar_indices]

        # Predict based on most common deployment type
        deployment_prediction = Counter(similar_deployments).most_common(1)[0][0]

        return deployment_prediction


# Example usage
if __name__ == "__main__":
    predictor = DeploymentPredictor("dataset.csv")
    sample_repo = "excalidraw/excalidraw"  # Replace with actual repository
    predicted_deployment = predictor.predict_deployment(sample_repo, n_similar=5)

    print(f"\nPredicted deployment type for {sample_repo}: {predicted_deployment}")

    predicted_deployment = predictor.predict_from_vector(
        [1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], n_similar=5
    )

    print(f"\nPredicted deployment type for custom vec: {predicted_deployment}")
