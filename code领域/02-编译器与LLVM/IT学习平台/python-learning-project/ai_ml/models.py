import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, mean_squared_error
from typing import Tuple, Dict


class SimpleLinearRegression:
    
    def __init__(self):
        self.slope = 0
        self.intercept = 0
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        x_mean = np.mean(X)
        y_mean = np.mean(y)
        
        numerator = np.sum((X - x_mean) * (y - y_mean))
        denominator = np.sum((X - x_mean) ** 2)
        
        self.slope = numerator / denominator
        self.intercept = y_mean - self.slope * x_mean
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.slope * X + self.intercept


class ModelTrainer:
    
    @staticmethod
    def generate_sample_data(n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        np.random.seed(42)
        X = np.random.randn(n_samples, 1) * 2 + 1
        y = 3 * X.flatten() + 2 + np.random.randn(n_samples) * 0.5
        return X, y
    
    @staticmethod
    def train_linear_regression(X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Dict:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        return {
            'model': model,
            'mse': mean_squared_error(y_test, y_pred),
            'r2_score': model.score(X_test, y_test),
            'coefficients': {'slope': model.coef_[0], 'intercept': model.intercept_}
        }
    
    @staticmethod
    def train_logistic_regression(X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Dict:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        model = LogisticRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        return {
            'model': model,
            'accuracy': accuracy_score(y_test, y_pred),
            'predictions': y_pred
        }


class ClassificationModel:
    
    @staticmethod
    def generate_classification_data(n_samples: int = 1000, n_features: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        from sklearn.datasets import make_classification
        X, y = make_classification(n_samples=n_samples, n_features=n_features, n_classes=2, random_state=42)
        return X, y
    
    @staticmethod
    def train_decision_tree(X: np.ndarray, y: np.ndarray, max_depth: int = 5) -> Dict:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        return {
            'model': model,
            'accuracy': accuracy_score(y_test, y_pred),
            'feature_importance': dict(zip(range(X.shape[1]), model.feature_importances_))
        }
    
    @staticmethod
    def train_random_forest(X: np.ndarray, y: np.ndarray, n_estimators: int = 100) -> Dict:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        return {
            'model': model,
            'accuracy': accuracy_score(y_test, y_pred),
            'feature_importance': dict(zip(range(X.shape[1]), model.feature_importances_))
        }


class NeuralNetwork:
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        self.weights1 = np.random.randn(input_size, hidden_size) * 0.01
        self.bias1 = np.zeros((1, hidden_size))
        self.weights2 = np.random.randn(hidden_size, output_size) * 0.01
        self.bias2 = np.zeros((1, output_size))
    
    def sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-x))
    
    def sigmoid_derivative(self, x: np.ndarray) -> np.ndarray:
        return x * (1 - x)
    
    def forward(self, X: np.ndarray) -> np.ndarray:
        self.hidden = self.sigmoid(np.dot(X, self.weights1) + self.bias1)
        output = self.sigmoid(np.dot(self.hidden, self.weights2) + self.bias2)
        return output
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 1000, learning_rate: float = 0.1):
        for epoch in range(epochs):
            output = self.forward(X)
            
            error = y - output
            d_output = error * self.sigmoid_derivative(output)
            
            error_hidden = d_output.dot(self.weights2.T)
            d_hidden = error_hidden * self.sigmoid_derivative(self.hidden)
            
            self.weights2 += self.hidden.T.dot(d_output) * learning_rate
            self.bias2 += np.sum(d_output, axis=0, keepdims=True) * learning_rate
            self.weights1 += X.T.dot(d_hidden) * learning_rate
            self.bias1 += np.sum(d_hidden, axis=0, keepdims=True) * learning_rate