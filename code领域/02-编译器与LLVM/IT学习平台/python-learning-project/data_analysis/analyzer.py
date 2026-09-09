import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple


class DataAnalyzer:
    
    @staticmethod
    def load_data(filepath: str) -> pd.DataFrame:
        return pd.read_csv(filepath)
    
    @staticmethod
    def generate_sample_data(n: int = 1000) -> pd.DataFrame:
        np.random.seed(42)
        data = {
            'id': range(1, n + 1),
            'value': np.random.randn(n),
            'category': np.random.choice(['A', 'B', 'C'], n),
            'timestamp': pd.date_range('2024-01-01', periods=n, freq='H')
        }
        return pd.DataFrame(data)
    
    @staticmethod
    def basic_statistics(df: pd.DataFrame) -> Dict:
        return {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_summary': df.describe().to_dict()
        }
    
    @staticmethod
    def filter_data(df: pd.DataFrame, column: str, condition) -> pd.DataFrame:
        return df[condition(df[column])]


class DataVisualizer:
    
    @staticmethod
    def plot_histogram(df: pd.DataFrame, column: str, bins: int = 30):
        plt.figure(figsize=(10, 6))
        plt.hist(df[column], bins=bins, edgecolor='black')
        plt.title(f'Histogram of {column}')
        plt.xlabel(column)
        plt.ylabel('Frequency')
        plt.savefig('docs/histogram.png')
        plt.close()
    
    @staticmethod
    def plot_scatter(df: pd.DataFrame, x: str, y: str):
        plt.figure(figsize=(10, 6))
        plt.scatter(df[x], df[y])
        plt.title(f'{x} vs {y}')
        plt.xlabel(x)
        plt.ylabel(y)
        plt.savefig('docs/scatter.png')
        plt.close()
    
    @staticmethod
    def plot_boxplot(df: pd.DataFrame, column: str):
        plt.figure(figsize=(10, 6))
        sns.boxplot(df[column])
        plt.title(f'Boxplot of {column}')
        plt.savefig('docs/boxplot.png')
        plt.close()
    
    @staticmethod
    def plot_correlation_heatmap(df: pd.DataFrame):
        numeric_df = df.select_dtypes(include=[np.number])
        correlation_matrix = numeric_df.corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
        plt.title('Correlation Heatmap')
        plt.savefig('docs/correlation_heatmap.png')
        plt.close()


class DataProcessor:
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna().drop_duplicates()
    
    @staticmethod
    def normalize_data(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        df_normalized = df.copy()
        for col in columns:
            if col in df_normalized.columns and df_normalized[col].dtype in ['int64', 'float64']:
                mean = df_normalized[col].mean()
                std = df_normalized[col].std()
                df_normalized[col] = (df_normalized[col] - mean) / std
        return df_normalized
    
    @staticmethod
    def aggregate_data(df: pd.DataFrame, group_by: List[str], agg_func: Dict) -> pd.DataFrame:
        return df.groupby(group_by).agg(agg_func).reset_index()