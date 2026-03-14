"""
Expense categorizer using ML algorithms
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import re
import os
from typing import Tuple, List, Dict, Any
import warnings
warnings.filterwarnings('ignore')


class ExpenseCategorizer:
    """
    ML model for automatically categorizing expense transactions
    """
    def __init__(self):
        self.pipeline = None
        self.categories = [
            'Food', 'Transportation', 'Housing', 'Entertainment',
            'Healthcare', 'Shopping', 'Travel', 'Education', 'Salary', 'Investment'
        ]
        self.is_trained = False

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess transaction description text
        """
        if not isinstance(text, str):
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    def create_sample_data(self) -> Tuple[List[str], List[str]]:
        """
        Create sample training data for demonstration
        In a real application, you would load actual training data
        """
        descriptions = [
            # Food
            "grocery shopping", "bought groceries", "supermarket purchase", "weekly food shopping",
            "restaurant dinner", "takeout food", "pizza delivery", "coffee shop",
            "bread", "milk", "eggs", "fruits", "vegetables", "meat", "chicken", "rice",
            "pasta", "cereal", "cheese", "yogurt", "snacks", "soda", "juice", "butter",
            "cheese", "apples", "bananas", "oranges", "potatoes", "onions", "bread rolls",
            "baguette", "wheat bread", "white bread", "whole grain bread", "baked goods",

            # Transportation
            "gas station", "fuel refill", "car gas", "petrol purchase",
            "bus fare", "train ticket", "uber ride", "taxi fare",

            # Housing
            "rent payment", "mortgage payment", "house rent", "apartment rent",
            "electricity bill", "water bill", "utility payment", "internet bill",

            # Entertainment
            "movie ticket", "cinema visit", "concert ticket", "theater show",
            "video game", "streaming service", "gym membership", "spa treatment",

            # Healthcare
            "doctor visit", "medical appointment", "prescription drugs", "hospital visit",
            "health insurance", "medical bill", "pharmacy purchase", "dental visit",

            # Shopping
            "clothing store", "department store", "retail shopping", "electronics store",
            "book store", "gift purchase", "home goods", "furniture shopping",

            # Travel
            "flight ticket", "airline booking", "hotel reservation", "vacation trip",
            "travel agency", "tourist attraction", "car rental", "airport parking",

            # Education
            "tuition fee", "school fees", "textbooks", "course material",
            "education loan", "training course", "educational software", "school supplies",

            # Income
            "salary deposit", "monthly salary", "paycheck", "wages",
            "investment income", "dividend payment", "interest income", "bonus payment"
        ]

        labels = [
            # Food
            "Food", "Food", "Food", "Food",
            "Food", "Food", "Food", "Food",
            "Food", "Food", "Food", "Food", "Food", "Food", "Food", "Food",
            "Food", "Food", "Food", "Food", "Food", "Food", "Food", "Food",
            "Food", "Food", "Food", "Food", "Food", "Food",
            "Food", "Food", "Food", "Food", "Food", "Food",

            # Transportation
            "Transportation", "Transportation", "Transportation", "Transportation",
            "Transportation", "Transportation", "Transportation", "Transportation",

            # Housing
            "Housing", "Housing", "Housing", "Housing",
            "Housing", "Housing", "Housing", "Housing",

            # Entertainment
            "Entertainment", "Entertainment", "Entertainment", "Entertainment",
            "Entertainment", "Entertainment", "Entertainment", "Entertainment",

            # Healthcare
            "Healthcare", "Healthcare", "Healthcare", "Healthcare",
            "Healthcare", "Healthcare", "Healthcare", "Healthcare",

            # Shopping
            "Shopping", "Shopping", "Shopping", "Shopping",
            "Shopping", "Shopping", "Shopping", "Shopping",

            # Travel
            "Travel", "Travel", "Travel", "Travel",
            "Travel", "Travel", "Travel", "Travel",

            # Education
            "Education", "Education", "Education", "Education",
            "Education", "Education", "Education", "Education",

            # Income
            "Salary", "Salary", "Salary", "Salary",
            "Investment", "Investment", "Investment", "Investment"
        ]

        return descriptions, labels

    def train(self, descriptions: List[str] = None, labels: List[str] = None, test_size: float = 0.2):
        """
        Train the expense categorization model
        """
        if descriptions is None or labels is None:
            # Use sample data if none provided
            descriptions, labels = self.create_sample_data()

        # Preprocess the descriptions
        processed_descriptions = [self.preprocess_text(desc) for desc in descriptions]

        # Create pipeline with TF-IDF vectorizer and Logistic Regression
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english')),
            ('classifier', LogisticRegression(random_state=42, max_iter=1000))
        ])

        # Split data for training and testing
        X_train, X_test, y_train, y_test = train_test_split(
            processed_descriptions, labels, test_size=test_size, random_state=42, stratify=labels
        )

        # Train the model
        self.pipeline.fit(X_train, y_train)

        # Evaluate the model
        y_pred = self.pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"Model trained with accuracy: {accuracy:.2f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        self.is_trained = True
        return accuracy

    def predict(self, description: str) -> Tuple[str, float]:
        """
        Predict the category for a transaction description
        Returns (category, confidence_score)
        """
        if not self.is_trained or self.pipeline is None:
            raise ValueError("Model must be trained before making predictions")

        if not description or not isinstance(description, str):
            return "Unknown", 0.0

        # Preprocess the description
        processed_desc = self.preprocess_text(description)

        # Predict the category
        predicted_category = self.pipeline.predict([processed_desc])[0]

        # Get prediction probabilities for confidence score
        probabilities = self.pipeline.predict_proba([processed_desc])[0]
        max_prob = max(probabilities)

        return predicted_category, float(max_prob)

    def save_model(self, filepath: str = "backend/ml_models/trained_models/expense_categorizer.pkl"):
        """
        Save the trained model to a file
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'wb') as f:
            pickle.dump({
                'pipeline': self.pipeline,
                'categories': self.categories,
                'is_trained': self.is_trained
            }, f)

    def load_model(self, filepath: str = "backend/ml_models/trained_models/expense_categorizer.pkl"):
        """
        Load a trained model from a file
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.pipeline = model_data['pipeline']
        self.categories = model_data['categories']
        self.is_trained = model_data['is_trained']

    def get_available_categories(self) -> List[str]:
        """
        Get list of available categories
        """
        return self.categories.copy()


if __name__ == "__main__":
    # Example usage
    categorizer = ExpenseCategorizer()

    # Train the model
    print("Training the expense categorizer...")
    accuracy = categorizer.train()

    # Test some predictions
    test_descriptions = [
        "bought groceries at walmart",
        "gas for the car",
        "rent payment",
        "movie night with friends",
        "doctor appointment"
    ]

    print("\nTest predictions:")
    for desc in test_descriptions:
        category, confidence = categorizer.predict(desc)
        print(f"Description: '{desc}' -> Category: {category} (Confidence: {confidence:.2f})")

    # Save the model
    categorizer.save_model()
    print(f"\nModel saved. Accuracy: {accuracy:.2f}")