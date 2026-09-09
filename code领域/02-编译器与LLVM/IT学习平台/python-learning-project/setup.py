from setuptools import setup, find_packages

setup(
    name="python-learning-project",
    version="0.1.0",
    description="综合Python学习项目",
    author="Your Name",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
        "ml": [
            "scikit-learn>=1.3.0",
            "torch>=2.0.0",
            "tensorflow>=2.13.0",
        ],
        "web": [
            "flask>=3.0.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
        ],
    },
)