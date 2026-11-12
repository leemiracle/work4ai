<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ML-For-Beginners · page 2 Core ML Concepts · fetched 2026-10-26 -->

# Core ML Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [1-Introduction/1-intro-to-ML/README.md](1-Introduction/1-intro-to-ML/README.md)
- [1-Introduction/2-history-of-ML/README.md](1-Introduction/2-history-of-ML/README.md)
- [1-Introduction/4-techniques-of-ML/README.md](1-Introduction/4-techniques-of-ML/README.md)
- [1-Introduction/4-techniques-of-ML/assignment.md](1-Introduction/4-techniques-of-ML/assignment.md)
- [1-Introduction/4-techniques-of-ML/images/overfitting.png](1-Introduction/4-techniques-of-ML/images/overfitting.png)
- [1-Introduction/README.md](1-Introduction/README.md)
- [1-Introduction/images/globe.jpg](1-Introduction/images/globe.jpg)
- [2-Regression/README.md](2-Regression/README.md)
- [5-Clustering/README.md](5-Clustering/README.md)
- [README.md](README.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [images/3.png](images/3.png)
- [quiz-app/src/assets/translations/en.json](quiz-app/src/assets/translations/en.json)

</details>



This document provides an overview of the fundamental machine learning concepts covered in the ML-For-Beginners curriculum. It introduces the core principles, terminology, and processes that form the foundation for all machine learning systems. The material is meant to bridge the introduction to ML with the specific learning paradigms explored in later sections. For detailed information about specific ML implementations, see [Supervised Learning](#3), [Unsupervised Learning](#4), and [Specialized ML Applications](#5).

## The Machine Learning Process

Machine learning follows a structured workflow from problem formulation to model deployment. Understanding this process is essential for developing effective ML solutions.

### The ML Workflow

```mermaid
flowchart LR
    A["Define Question"] --> B["Collect Data"]
    B --> C["Prepare Data"]
    C --> D["Split Dataset"]
    D --> E["Choose Training Method"]
    E --> F["Train Model (model.fit)"]
    F --> G["Evaluate Model"]
    G --> H["Parameter Tuning"]
    H --> I["Make Predictions"]
    G -- "If performance is poor" --> H
    H -- "If performance improves" --> F
    H -- "If performance is acceptable" --> I
```

The process begins with a specific question that cannot be easily answered with rule-based programming. Data collection and preparation follow, leading to model training, evaluation, and refinement before using the model to make predictions on new data.

Sources: [1-Introduction/4-techniques-of-ML/README.md:16-24](). [1-Introduction/4-techniques-of-ML/README.md:98-101]().

## Key ML Terminology

### Features and Target Variables

```mermaid
flowchart LR
    A["Dataset"] --> B["Features (X)"]
    A --> C["Target (y)"]
    
    B -- "Input to model" --> D["ML Model"]
    D -- "Predicts" --> C
    
    subgraph "sklearn syntax"
        E["X_train, X_test"]
        F["y_train, y_test"]
    end
    
    B -.-> E
    C -.-> F
```

- **Features**: Measurable properties of your data (independent variables), represented as `X` in code
- **Target**: What you're trying to predict (dependent variable), represented as `y` in code

Features are the inputs to your model, while the target is what the model learns to predict.

Sources: [1-Introduction/4-techniques-of-ML/README.md:48-51]().

### Dataset Splitting

```mermaid
flowchart TD
    A["Complete Dataset"] --> B["train_test_split()"]
    
    B --> C["Training Data (70-80%)"]
    B --> D["Testing Data (20-30%)"]
    
    C -- "model.fit(X_train, y_train)" --> E["Model Training"]
    E --> F["Trained Model"]
    
    F -- "model.predict(X_test)" --> G["Predictions"]
    
    D -- "y_test (actual values)" --> H["Evaluation Metrics"]
    G -- "ŷ (predicted values)" --> H
    
    subgraph "Optional Validation"
        C --> I["Validation Data"]
        I -- "Hyperparameter Tuning" --> E
    end
```

Data is typically split into:
- **Training data**: Used to fit the model (70-80% of data)
- **Testing data**: Used to evaluate the model's performance on unseen data (20-30%)
- **Validation data**: Optional split used for hyperparameter tuning

In scikit-learn, this is implemented using the `train_test_split` function.

Sources: [1-Introduction/4-techniques-of-ML/README.md:61-67]().

## Learning Paradigms

Machine learning encompasses several learning paradigms that differ in their approach and application.

### ML Paradigms Overview

```mermaid
flowchart TD
    ML["Machine Learning"] --> SL["Supervised Learning"]
    ML --> UL["Unsupervised Learning"]
    ML --> RL["Reinforcement Learning"]
    
    SL --> Reg["Regression"]
    SL --> Class["Classification"]
    
    Reg --> LR["Linear Regression
    (sklearn.linear_model)"]
    Reg --> LogR["Logistic Regression
    (sklearn.linear_model)"]
    
    Class --> DT["Decision Trees
    (sklearn.tree)"]
    Class --> SVM["Support Vector Machines
    (sklearn.svm)"]
    
    UL --> Clust["Clustering"]
    UL --> DR["Dimensionality Reduction"]
    
    Clust --> KM["K-Means
    (sklearn.cluster.KMeans)"]
    
    RL --> QL["Q-Learning"]
    
    ML --> Other["Specialized Applications"]
    Other --> NLP["Natural Language Processing"]
    Other --> TS["Time Series Forecasting"]
```

Sources: [1-Introduction/1-intro-to-ML/translations/README.fr.md:50-61](). [1-Introduction/4-techniques-of-ML/README.md:70-76]().

### Supervised Learning

Supervised learning involves training a model on labeled data to make predictions. The model learns to map input features to known output values.

| Type | Purpose | Examples | Target Type |
|------|---------|----------|------------|
| Regression | Predict continuous values | House price prediction, temperature forecasting | Numeric |
| Classification | Predict categories or classes | Email spam detection, image recognition | Categorical |

For more details, see [Supervised Learning](#3), [Regression](#3.1), and [Classification](#3.2).

Sources: [1-Introduction/1-intro-to-ML/translations/README.fr.md:54-56]().

### Unsupervised Learning

Unsupervised learning involves finding patterns or structure in unlabeled data. The model identifies inherent groupings or patterns without predefined outputs.

| Type | Purpose | Examples |
|------|---------|----------|
| Clustering | Group similar data points | Customer segmentation, anomaly detection |
| Dimensionality Reduction | Reduce feature space | Data compression, visualization |

For more details, see [Unsupervised Learning](#4) and [Clustering](#4.1).

Sources: [1-Introduction/1-intro-to-ML/translations/README.fr.md:57]().

### Specialized Applications

Beyond the fundamental paradigms, machine learning has specialized applications in various domains:

- **Natural Language Processing (NLP)**: Working with text data
- **Time Series Forecasting**: Predicting future values based on sequential data
- **Reinforcement Learning**: Learning through interaction with an environment

For more details, see [Specialized ML Applications](#5).

Sources: [1-Introduction/1-intro-to-ML/translations/README.fr.md:58-60]().

## Model Training and Evaluation

### Model Fitting

```mermaid
flowchart LR
    A["Underfitting"] --> B["Good Fit"] --> C["Overfitting"]
    
    subgraph "Training Error vs Testing Error"
        D["High Training Error
        High Testing Error"] --- E["Low Training Error
        Low Testing Error"] --- F["Low Training Error
        High Testing Error"]
    end
    
    A --- D
    B --- E
    C --- F
    
    G["model.fit(X_train, y_train)"] --> B
```

- **Underfitting**: Model is too simple to capture the underlying pattern in the data
- **Good fit**: Model generalizes well to unseen data
- **Overfitting**: Model learns the noise in the training data and performs poorly on new data

Sources: [1-Introduction/4-techniques-of-ML/README.md:86-90]().

### Model Evaluation Metrics

Model performance is assessed using various metrics depending on the learning paradigm:

| Learning Type | Common Metrics | Scikit-learn Implementation |
|---------------|----------------|----------------------------|
| Regression | Mean Squared Error (MSE), Root Mean Squared Error (RMSE), Mean Absolute Error (MAE) | `sklearn.metrics.mean_squared_error`, `sklearn.metrics.mean_absolute_error` |
| Classification | Accuracy, Precision, Recall, F1 Score, ROC-AUC | `sklearn.metrics.accuracy_score`, `sklearn.metrics.precision_recall_fscore_support`, `sklearn.metrics.roc_auc_score` |
| Clustering | Silhouette Score, Davies-Bouldin Index | `sklearn.metrics.silhouette_score`, `sklearn.metrics.davies_bouldin_score` |

Sources: [1-Introduction/4-techniques-of-ML/README.md:80-84]().

### Parameter Tuning

Improving model performance often involves adjusting hyperparameters, which are values set before training begins. This process may include:

- Grid Search: Testing all possible combinations of parameters
- Random Search: Testing random combinations of parameters
- Cross-Validation: Using multiple train-test splits to validate parameter choices

In scikit-learn, this can be implemented using `GridSearchCV` or `RandomizedSearchCV`.

Sources: [1-Introduction/4-techniques-of-ML/README.md:94-96]().

## Responsible AI in Machine Learning

Machine learning solutions should be built with responsible AI principles in mind. These principles ensure that ML systems are fair, reliable, inclusive, secure, transparent, and accountable.

```mermaid
flowchart TD
    A["Responsible AI Principles"] --> B["Fairness"]
    A --> C["Reliability & Safety"]
    A --> D["Inclusiveness"]
    A --> E["Security & Privacy"]
    A --> F["Transparency"]
    A --> G["Accountability"]
    
    B --> B1["Mitigate bias in data and models"]
    C --> C1["Ensure consistent performance in varied conditions"]
    D --> D1["Design for all users regardless of ability"]
    E --> E1["Protect sensitive information"]
    F --> F1["Explain model decisions"]
    G --> G1["Take responsibility for AI outcomes"]
```

### Impact Assessment and Debugging

When implementing ML solutions, consider:

- **Adverse impact on individuals**: Identify potential harms from system use
- **Data requirements**: Understand regulatory and quality requirements
- **Fairness analysis**: Evaluate for bias across different groups
- **Interpretability**: Understand what drives model outcomes

Sources: [1-Introduction/3-fairness/README.md:33-96](). [1-Introduction/3-fairness/README.md:97-117]().

## ML Technologies and Implementation

The curriculum primarily uses the following technologies for implementing machine learning concepts:

### Key Libraries

```mermaid
flowchart TD
    A["ML Implementation"] --> B["Python Ecosystem"]
    A --> C["Web Deployment"]
    
    B --> D["Scikit-learn
    Primary ML library"]
    B --> E["NumPy
    Numerical computations"]
    B --> F["Pandas
    Data manipulation"]
    B --> G["Matplotlib/Seaborn
    Visualization"]
    
    C --> H["Node.js/JavaScript
    Web interfaces"]
    
    D --> I["model = sklearn.linear_model.LinearRegression()
    model.fit(X, y)
    predictions = model.predict(X_new)"]
```

In this curriculum, you'll primarily work with:

- **Scikit-learn**: For implementing ML algorithms
- **Python**: As the primary programming language
- **JavaScript/Node.js**: For web application development

Sources: [1-Introduction/1-intro-to-ML/translations/README.fr.md:18-24]().

## Conclusion

This overview of core ML concepts provides the foundation for understanding the more detailed explorations of specific machine learning techniques in the subsequent sections of this curriculum. As you progress through the material, you'll build on these concepts and gain hands-on experience implementing various machine learning solutions.

Remember that effective machine learning requires not only technical skill but also careful consideration of responsible AI principles to ensure your solutions are beneficial, fair, and ethical.

For specific implementations and deeper exploration of these concepts, refer to the subsequent sections of this curriculum.

---

