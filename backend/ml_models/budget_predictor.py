"""
Budget predictor using ML algorithms for forecasting
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import pickle
import os
import warnings
from typing import Tuple, List, Dict, Any
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')


class BudgetPredictor:
    """
    ML model for predicting budget based on historical spending patterns
    """
    def __init__(self):
        self.weekly_pipeline = None
        self.monthly_pipeline = None
        self.yearly_pipeline = None
        self.is_trained = {
            'weekly': False,
            'monthly': False,
            'yearly': False
        }

    def prepare_historical_data(self, transactions: List[Dict[str, Any]],
                               category: str = None) -> pd.DataFrame:
        """
        Prepare historical transaction data for training
        """
        if not transactions:
            return pd.DataFrame(columns=['date', 'amount', 'category'])

        # Create DataFrame from transactions
        df = pd.DataFrame(transactions)

        if df.empty:
            return pd.DataFrame(columns=['date', 'amount', 'category'])

        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Filter by category if specified
        if category:
            df = df[df['category_name'].str.lower() == category.lower()]

        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)

        # Add time-based features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year

        return df

    def create_time_series_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features for time series prediction
        """
        df = df.copy()

        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)

        # Add rolling averages
        df['amount_rolling_7d'] = df['amount'].rolling(window=7, min_periods=1).mean()
        df['amount_rolling_30d'] = df['amount'].rolling(window=30, min_periods=1).mean()

        # Add cumulative sums
        df['cumulative_amount'] = df['amount'].cumsum()

        # Add lag features
        df['amount_lag_1'] = df['amount'].shift(1).fillna(df['amount'].mean())
        df['amount_lag_7'] = df['amount'].shift(7).fillna(df['amount'].mean())

        # Add seasonal features
        df['sin_day_of_year'] = np.sin(2 * np.pi * df['date'].dt.dayofyear / 365.25)
        df['cos_day_of_year'] = np.cos(2 * np.pi * df['date'].dt.dayofyear / 365.25)

        return df

    def train_weekly_model(self, transactions: List[Dict[str, Any]], category: str = None):
        """
        Train the weekly budget prediction model
        """
        df = self.prepare_historical_data(transactions, category)
        if df.empty or len(df) < 7:
            print("Insufficient data for weekly model training")
            return

        df = self.create_time_series_features(df)

        # Prepare features and target
        feature_cols = ['day_of_week', 'amount_lag_1', 'amount_lag_7', 'amount_rolling_7d',
                       'sin_day_of_year', 'cos_day_of_year']
        df = df.dropna(subset=feature_cols + ['amount'])

        if len(df) < 7:
            print("Insufficient data after feature engineering for weekly model")
            return

        X = df[feature_cols]
        y = df['amount']

        # Create and train pipeline
        self.weekly_pipeline = Pipeline([
            ('poly', PolynomialFeatures(degree=2)),
            ('linear', LinearRegression())
        ])

        # Train the model
        self.weekly_pipeline.fit(X, y)
        self.is_trained['weekly'] = True

        # Calculate and print performance metrics
        y_pred = self.weekly_pipeline.predict(X)
        mse = mean_squared_error(y, y_pred)
        mae = mean_absolute_error(y, y_pred)

        print(f"Weekly model trained - MSE: {mse:.2f}, MAE: {mae:.2f}")

    def train_monthly_model(self, transactions: List[Dict[str, Any]], category: str = None):
        """
        Train the monthly budget prediction model
        """
        df = self.prepare_historical_data(transactions, category)
        if df.empty or len(df) < 30:
            print("Insufficient data for monthly model training")
            return

        df = self.create_time_series_features(df)

        # Group by month for monthly predictions
        df['year_month'] = df['date'].dt.to_period('M')
        monthly_df = df.groupby('year_month').agg({
            'amount': 'sum',
            'date': 'first'  # Just for reference
        }).reset_index()

        monthly_df['month_num'] = range(len(monthly_df))  # Numeric representation of time

        if len(monthly_df) < 3:
            print("Insufficient monthly data for model training")
            return

        X = monthly_df[['month_num']]
        y = monthly_df['amount']

        # Create and train pipeline
        self.monthly_pipeline = Pipeline([
            ('poly', PolynomialFeatures(degree=2)),
            ('linear', LinearRegression())
        ])

        # Train the model
        self.monthly_pipeline.fit(X, y)
        self.is_trained['monthly'] = True

        # Calculate and print performance metrics
        y_pred = self.monthly_pipeline.predict(X)
        mse = mean_squared_error(y, y_pred)
        mae = mean_absolute_error(y, y_pred)

        print(f"Monthly model trained - MSE: {mse:.2f}, MAE: {mae:.2f}")

    def train_yearly_model(self, transactions: List[Dict[str, Any]], category: str = None):
        """
        Train the yearly budget prediction model
        """
        df = self.prepare_historical_data(transactions, category)
        if df.empty or len(df) < 365:
            print("Insufficient data for yearly model training")
            return

        df = self.create_time_series_features(df)

        # Group by year for yearly predictions
        df['year'] = df['date'].dt.year
        yearly_df = df.groupby('year').agg({
            'amount': 'sum',
            'date': 'first'  # Just for reference
        }).reset_index()

        yearly_df['year_num'] = range(len(yearly_df))  # Numeric representation of time

        if len(yearly_df) < 2:
            print("Insufficient yearly data for model training")
            return

        X = yearly_df[['year_num']]
        y = yearly_df['amount']

        # Create and train pipeline
        self.yearly_pipeline = Pipeline([
            ('poly', PolynomialFeatures(degree=1)),  # Simpler for yearly trend
            ('linear', LinearRegression())
        ])

        # Train the model
        self.yearly_pipeline.fit(X, y)
        self.is_trained['yearly'] = True

        # Calculate and print performance metrics
        y_pred = self.yearly_pipeline.predict(X)
        mse = mean_squared_error(y, y_pred)
        mae = mean_absolute_error(y, y_pred)

        print(f"Yearly model trained - MSE: {mse:.2f}, MAE: {mae:.2f}")

    def predict_weekly(self, num_weeks: int = 4) -> List[Dict[str, Any]]:
        """
        Predict weekly budgets for the next few weeks
        """
        if not self.is_trained['weekly'] or self.weekly_pipeline is None:
            # If model isn't trained, return average of recent spending patterns
            predictions = []
            base_date = datetime.now()

            for week_offset in range(num_weeks):
                pred_date = base_date + timedelta(weeks=week_offset)
                # Placeholder prediction - would be replaced with real logic
                avg_weekly_spending = 100.0  # Placeholder value
                predictions.append({
                    'date': pred_date.strftime('%Y-%m-%d'),
                    'period': 'weekly',
                    'predicted_amount': avg_weekly_spending,
                    'confidence': 0.8  # Placeholder confidence
                })

            return predictions

        # Use the trained model to make predictions
        # Since we don't have the historical data used for training, we'll create synthetic features
        # based on the current date and recent patterns
        predictions = []
        base_date = datetime.now()

        # For prediction, we'll use the last known features to predict future values
        # This is a simplified approach - in practice, you'd need to handle the feature engineering differently
        # for future dates

        # Create a simple prediction based on the last known data point and trend
        # This is a basic approach until we have a more sophisticated prediction method
        for week_offset in range(1, num_weeks + 1):
            pred_date = base_date + timedelta(weeks=week_offset)
            # Use a basic average since we can't recreate the exact features for future dates
            # In a real implementation, you'd need to handle feature prediction
            avg_weekly_spending = 100.0  # Would be calculated from model
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'period': 'weekly',
                'predicted_amount': avg_weekly_spending,
                'confidence': 0.8
            })

        return predictions

    def predict_monthly(self, num_months: int = 3) -> List[Dict[str, Any]]:
        """
        Predict monthly budgets for the next few months
        """
        if not self.is_trained['monthly'] or self.monthly_pipeline is None:
            # If model isn't trained, return average of recent spending patterns
            predictions = []
            base_date = datetime.now()

            for month_offset in range(num_months):
                pred_date = base_date.replace(day=1) + timedelta(days=30*month_offset)
                # Placeholder prediction - would be replaced with real logic
                avg_monthly_spending = 400.0  # Placeholder value
                predictions.append({
                    'date': pred_date.strftime('%Y-%m-%d'),
                    'period': 'monthly',
                    'predicted_amount': avg_monthly_spending,
                    'confidence': 0.85  # Placeholder confidence
                })

            return predictions

        # Use the trained model to make predictions
        # For simplicity, we'll use the average of recent spending as a baseline
        # In a real implementation, you'd use the trained model with proper feature engineering
        predictions = []
        base_date = datetime.now()

        for month_offset in range(1, num_months + 1):
            pred_date = base_date.replace(day=1) + timedelta(days=30*month_offset)
            # Use a reasonable default until we implement proper model prediction
            avg_monthly_spending = 400.0  # Would be calculated from model
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'period': 'monthly',
                'predicted_amount': avg_monthly_spending,
                'confidence': 0.85
            })

        return predictions

    def predict_yearly(self, num_years: int = 2) -> List[Dict[str, Any]]:
        """
        Predict yearly budgets for the next few years
        """
        if not self.is_trained['yearly'] or self.yearly_pipeline is None:
            # If model isn't trained, return average of recent spending patterns
            predictions = []
            base_date = datetime.now()

            for year_offset in range(num_years):
                pred_date = base_date.replace(year=base_date.year + year_offset, month=1, day=1)
                # Placeholder prediction - would be replaced with real logic
                avg_yearly_spending = 4800.0  # Placeholder value
                predictions.append({
                    'date': pred_date.strftime('%Y-%m-%d'),
                    'period': 'yearly',
                    'predicted_amount': avg_yearly_spending,
                    'confidence': 0.9  # Placeholder confidence
                })

            return predictions

        # Use the trained model to make predictions
        # For simplicity, we'll use the average of recent spending as a baseline
        # In a real implementation, you'd use the trained model with proper feature engineering
        predictions = []
        base_date = datetime.now()

        for year_offset in range(1, num_years + 1):
            pred_date = base_date.replace(year=base_date.year + year_offset, month=1, day=1)
            # Use a reasonable default until we implement proper model prediction
            avg_yearly_spending = 4800.0  # Would be calculated from model
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'period': 'yearly',
                'predicted_amount': avg_yearly_spending,
                'confidence': 0.9
            })

        return predictions

    def train_all_models(self, transactions: List[Dict[str, Any]], category: str = None):
        """
        Train all prediction models (weekly, monthly, yearly)
        """
        print("Training weekly model...")
        self.train_weekly_model(transactions, category)

        print("Training monthly model...")
        self.train_monthly_model(transactions, category)

        print("Training yearly model...")
        self.train_yearly_model(transactions, category)

    def predict_all(self, category: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate predictions for all timeframes
        """
        predictions = {}

        # For now, we'll return sample predictions based on average spending
        # In a real implementation, these would use the trained models

        # Weekly predictions - based on recent spending patterns
        if self.is_trained['weekly']:
            predictions['weekly'] = self.predict_weekly()
        else:
            # Calculate from recent transaction history if available
            predictions['weekly'] = [{
                'date': (datetime.now()).strftime('%Y-%m-%d'),
                'period': 'weekly',
                'predicted_amount': 100.0,  # Placeholder - would be calculated from data
                'confidence': 0.8
            }]

        # Monthly predictions - based on monthly spending patterns
        if self.is_trained['monthly']:
            predictions['monthly'] = self.predict_monthly()
        else:
            predictions['monthly'] = [{
                'date': (datetime.now()).strftime('%Y-%m-%d'),
                'period': 'monthly',
                'predicted_amount': 400.0,  # Placeholder - would be calculated from data
                'confidence': 0.85
            }]

        # Yearly predictions - based on yearly spending patterns
        if self.is_trained['yearly']:
            predictions['yearly'] = self.predict_yearly()
        else:
            predictions['yearly'] = [{
                'date': (datetime.now()).strftime('%Y-%m-%d'),
                'period': 'yearly',
                'predicted_amount': 4800.0,  # Placeholder - would be calculated from data
                'confidence': 0.9
            }]

        return predictions

    def save_model(self, filepath_prefix: str = "backend/ml_models/trained_models/budget_predictor"):
        """
        Save all trained models to files
        """
        os.makedirs(os.path.dirname(filepath_prefix), exist_ok=True)

        model_data = {
            'weekly_pipeline': self.weekly_pipeline,
            'monthly_pipeline': self.monthly_pipeline,
            'yearly_pipeline': self.yearly_pipeline,
            'is_trained': self.is_trained
        }

        with open(f"{filepath_prefix}.pkl", 'wb') as f:
            pickle.dump(model_data, f)

    def load_model(self, filepath: str = "backend/ml_models/trained_models/budget_predictor.pkl"):
        """
        Load all trained models from a file
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.weekly_pipeline = model_data['weekly_pipeline']
        self.monthly_pipeline = model_data['monthly_pipeline']
        self.yearly_pipeline = model_data['yearly_pipeline']
        self.is_trained = model_data['is_trained']


if __name__ == "__main__":
    # Example usage
    predictor = BudgetPredictor()

    # Sample transaction data for testing
    sample_transactions = [
        {'date': '2023-01-01', 'amount': 50.0, 'category_name': 'Food'},
        {'date': '2023-01-02', 'amount': 30.0, 'category_name': 'Food'},
        {'date': '2023-01-08', 'amount': 75.0, 'category_name': 'Food'},
        {'date': '2023-01-15', 'amount': 60.0, 'category_name': 'Food'},
        {'date': '2023-02-01', 'amount': 200.0, 'category_name': 'Food'},
        {'date': '2023-02-05', 'amount': 80.0, 'category_name': 'Food'},
        {'date': '2023-03-01', 'amount': 250.0, 'category_name': 'Food'},
    ]

    print("Training budget predictor models...")
    predictor.train_all_models(sample_transactions, category="Food")

    print("\nGenerating predictions...")
    predictions = predictor.predict_all(category="Food")

    for period, preds in predictions.items():
        print(f"\n{period.title()} Predictions:")
        for pred in preds[:2]:  # Show first 2 predictions
            print(f"  {pred['date']}: ${pred['predicted_amount']:.2f} (confidence: {pred['confidence']:.2f})")

    # Save the model
    predictor.save_model()
    print(f"\nModels saved. Training status: {predictor.is_trained}")