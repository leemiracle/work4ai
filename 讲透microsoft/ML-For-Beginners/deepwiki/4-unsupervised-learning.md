<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ML-For-Beginners · page 4 Unsupervised Learning · fetched 2026-10-26 -->

# Unsupervised Learning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [5-Clustering/1-Visualize/README.md](5-Clustering/1-Visualize/README.md)
- [5-Clustering/2-K-Means/README.md](5-Clustering/2-K-Means/README.md)
- [6-NLP/1-Introduction-to-NLP/README.md](6-NLP/1-Introduction-to-NLP/README.md)
- [6-NLP/1-Introduction-to-NLP/images/comprehension.png](6-NLP/1-Introduction-to-NLP/images/comprehension.png)
- [6-NLP/2-Tasks/README.md](6-NLP/2-Tasks/README.md)
- [6-NLP/3-Translation-Sentiment/README.md](6-NLP/3-Translation-Sentiment/README.md)
- [6-NLP/3-Translation-Sentiment/images/monnaie.png](6-NLP/3-Translation-Sentiment/images/monnaie.png)
- [6-NLP/4-Hotel-Reviews-1/README.md](6-NLP/4-Hotel-Reviews-1/README.md)
- [6-NLP/5-Hotel-Reviews-2/README.md](6-NLP/5-Hotel-Reviews-2/README.md)
- [6-NLP/5-Hotel-Reviews-2/assignment.md](6-NLP/5-Hotel-Reviews-2/assignment.md)
- [6-NLP/5-Hotel-Reviews-2/solution/3-notebook.ipynb](6-NLP/5-Hotel-Reviews-2/solution/3-notebook.ipynb)
- [6-NLP/README.md](6-NLP/README.md)

</details>



## Purpose and Scope

This document covers the unsupervised learning module within the ML-For-Beginners curriculum, specifically focusing on clustering techniques for discovering patterns in unlabeled data. The primary implementation uses K-Means clustering applied to a Nigerian music dataset to group similar songs based on audio features. For supervised learning approaches using labeled data, see [Supervised Learning](#3). For natural language processing applications, see [Specialized ML Applications](#5).

## Overview of Unsupervised Learning

Unsupervised learning algorithms discover patterns in unlabeled datasets where inputs are not matched with predefined outputs. Unlike supervised approaches that learn from labeled examples, unsupervised methods group or structure data based on inherent similarities without prior knowledge of categories.

The curriculum implements clustering as the primary unsupervised technique, where data points are partitioned into groups (clusters) such that points within a cluster are more similar to each other than to points in other clusters.

Sources: [5-Clustering/1-Visualize/README.md:1-15]()

## Clustering Fundamentals

### Clustering Definition and Use Cases

Clustering partitions a dataset into groups by examining patterns and relationships without requiring labeled training data. The algorithm assigns cluster IDs to data points, enabling pattern discovery while preserving privacy (referencing data by cluster ID rather than identifying information).

**Common Applications:**
- Market segmentation (age groups, purchasing patterns)
- Anomaly detection (fraud detection in credit card transactions)
- Medical diagnosis (tumor detection in scan batches)
- Search result grouping (shopping links, images, reviews)

Sources: [5-Clustering/1-Visualize/README.md:13-30]()

### Clustering Algorithm Selection

The curriculum uses scikit-learn's clustering implementations. Algorithm selection depends on data characteristics:

| Algorithm | Use Case | Type |
|-----------|----------|------|
| K-Means | General purpose | Inductive, centroid-based |
| Affinity Propagation | Many uneven clusters | Inductive |
| Mean-shift | Many uneven clusters | Inductive |
| Spectral Clustering | Few even clusters | Transductive |
| DBSCAN | Non-flat geometry, uneven clusters | Transductive, density-based |
| Hierarchical | Many constrained clusters | Transductive |

**Key Concepts:**

- **Transductive vs Inductive**: Transductive methods map observed training cases to specific test cases; inductive methods derive general rules applied to new test cases
- **Flat vs Non-flat Geometry**: Flat geometry uses Euclidean distance; non-flat uses curved distance measurements for data not existing on a plane
- **Constrained Clustering**: Semi-supervised approach forcing "must-link" or "cannot-link" relationships between points

Sources: [5-Clustering/1-Visualize/README.md:32-79]()

### Clustering Algorithm Types

```mermaid
graph TB
    subgraph "Clustering Methods"
        HIER["Hierarchical Clustering<br/>Distance-based grouping"]
        CENT["Centroid Clustering<br/>K-Means, center points"]
        DIST["Distribution-based<br/>Gaussian mixtures"]
        DENS["Density-based<br/>DBSCAN, OPTICS"]
        GRID["Grid-based<br/>Multi-dimensional cells"]
    end
    
    subgraph "Implementation"
        KMEANS["KMeans class<br/>sklearn.cluster.KMeans"]
        FIT["fit() method"]
        PRED["predict() method"]
        SCORE["silhouette_score()"]
    end
    
    CENT --> KMEANS
    KMEANS --> FIT
    KMEANS --> PRED
    KMEANS --> SCORE
    
    subgraph "Distance Metrics"
        EUCLID["Euclidean Distance<br/>Centroid calculation"]
        CLUSTROID["Clustroid<br/>Closest point to others"]
    end
    
    CENT --> EUCLID
    HIER --> CLUSTROID
```

Sources: [5-Clustering/1-Visualize/README.md:80-99]()

## Dataset and Data Processing

### Nigerian Music Dataset

The clustering implementation uses `nigerian-songs.csv` containing 530 song records with audio features from three genres: afro dancehall, afropop, and nigerian pop.

**Dataset Structure:**

| Column | Type | Description |
|--------|------|-------------|
| name | object | Song title |
| artist_top_genre | object | Genre classification |
| popularity | int64 | Popularity score (0-73) |
| danceability | float64 | Danceability metric (0-1) |
| acousticness | float64 | Acoustic quality (0-1) |
| energy | float64 | Energy level (0-1) |
| loudness | float64 | Loudness in dB |
| tempo | float64 | Beats per minute |

Sources: [5-Clustering/1-Visualize/README.md:112-164]()

### Data Preparation Pipeline

```mermaid
graph LR
    subgraph "Data Loading"
        CSV["nigerian-songs.csv<br/>530 rows"]
        PANDAS["pd.read_csv()"]
        DF["DataFrame df"]
    end
    
    subgraph "Data Cleaning"
        INFO["df.info()<br/>Check dtypes"]
        NULL["df.isnull().sum()<br/>Verify no nulls"]
        DESC["df.describe()<br/>Statistical summary"]
        FILTER["Filter genres<br/>Remove 'Missing'"]
    end
    
    subgraph "Feature Selection"
        GENRE["artist_top_genre<br/>3 genres filtered"]
        POP["popularity > 0<br/>Remove unranked"]
        FEATURES["Select features:<br/>popularity, danceability<br/>acousticness, loudness, energy"]
    end
    
    subgraph "Encoding"
        LABEL["LabelEncoder"]
        ENCODE["fit_transform()<br/>Genre to numeric"]
        X["Feature matrix X"]
        Y["Target array y"]
    end
    
    CSV --> PANDAS
    PANDAS --> DF
    DF --> INFO
    DF --> NULL
    DF --> DESC
    DF --> FILTER
    FILTER --> GENRE
    FILTER --> POP
    GENRE --> FEATURES
    POP --> FEATURES
    FEATURES --> LABEL
    LABEL --> ENCODE
    ENCODE --> X
    ENCODE --> Y
```

Sources: [5-Clustering/1-Visualize/README.md:132-277](), [5-Clustering/2-K-Means/README.md:38-102]()

### Data Exploration and Visualization

The preprocessing workflow includes exploratory visualization to understand data distribution and feature relationships:

```mermaid
graph TB
    subgraph "Visualization Methods"
        BOX["sns.boxplot()<br/>Outlier detection"]
        BAR["sns.barplot()<br/>Genre frequency"]
        CORR["df.corr()<br/>Feature correlation"]
        HEAT["sns.heatmap()<br/>Correlation matrix"]
    end
    
    subgraph "Distribution Analysis"
        JOINT["sns.jointplot()<br/>KDE plot<br/>popularity vs danceability"]
        FACET["sns.FacetGrid()<br/>Scatter by genre"]
        CONV["Concentric circles<br/>Show convergence"]
    end
    
    subgraph "Data Quality"
        OUT["Identify outliers<br/>via boxplots"]
        NOISE["Assess noise<br/>Check variance"]
        SKEW["Check imbalance<br/>Genre distribution"]
    end
    
    BOX --> OUT
    CORR --> HEAT
    JOINT --> CONV
    FACET --> CONV
    OUT --> NOISE
    BAR --> SKEW
```

**Key Findings:**
- Strongest correlation: energy and loudness (expected relationship)
- Data shows concentric convergence around danceability regardless of genre
- High variance and outliers present in multiple features
- Three genres loosely align in popularity/danceability space

Sources: [5-Clustering/1-Visualize/README.md:215-314](), [5-Clustering/2-K-Means/README.md:41-85]()

## K-Means Algorithm Implementation

### K-Means Algorithm Mechanics

K-Means clustering partitions data into k groups through an iterative three-step process:

1. **Initialization**: Select k center points by sampling from dataset
2. **Assignment Loop**:
   - Assign each sample to nearest centroid
   - Create new centroids from mean of assigned samples
   - Calculate difference between new and old centroids
   - Repeat until centroids stabilize

The algorithm minimizes inertia (within-cluster sum of squares), measuring internal cluster coherence.

Sources: [5-Clustering/2-K-Means/README.md:14-30]()

### Model Training Workflow

```mermaid
graph TB
    subgraph "Setup"
        IMPORT["from sklearn.cluster import KMeans"]
        NCLUSTERS["nclusters = 3<br/>Target cluster count"]
        SEED["random_state = 0<br/>Reproducibility"]
    end
    
    subgraph "Training"
        INIT["KMeans()<br/>init='k-means++'"]
        FIT["km.fit(X)<br/>Train on features"]
        PRED["km.predict(X)<br/>Assign clusters"]
        LABELS["y_cluster_kmeans<br/>Cluster assignments"]
    end
    
    subgraph "Evaluation"
        SIL["silhouette_score()<br/>Cluster quality"]
        SCORE["Score: -1 to 1<br/>1 = well separated"]
        WCSS["Within-cluster SS<br/>km.inertia_"]
    end
    
    subgraph "Optimization"
        RANGE["for i in range(1, 11)"]
        ELBOW["Elbow method<br/>Plot WCSS vs k"]
        OPTIMAL["Find 'elbow'<br/>Optimal k value"]
    end
    
    IMPORT --> NCLUSTERS
    NCLUSTERS --> SEED
    SEED --> INIT
    INIT --> FIT
    FIT --> PRED
    PRED --> LABELS
    LABELS --> SIL
    SIL --> SCORE
    FIT --> WCSS
    WCSS --> RANGE
    RANGE --> ELBOW
    ELBOW --> OPTIMAL
```

**Initialization Parameters:**

- `n_clusters`: Number of clusters to form
- `init='k-means++'`: Smart initialization placing centroids distant from each other for better convergence
- `random_state`: Seed for centroid initialization reproducibility
- `inertia_`: Sum of squared distances to nearest cluster center

Sources: [5-Clustering/2-K-Means/README.md:104-162]()

### Code Implementation

The K-Means training loop implements the elbow method to determine optimal cluster count:

```python
# Setup and iteration
from sklearn.cluster import KMeans
wcss = []

for i in range(1, 11):
    kmeans = KMeans(n_clusters = i, init = 'k-means++', random_state = 42)
    kmeans.fit(X)
    wcss.append(kmeans.inertia_)
```

Key implementation at [5-Clustering/2-K-Means/README.md:142-149]()

Final model training and prediction:

```python
# Train with optimal k=3
kmeans = KMeans(n_clusters = 3)
kmeans.fit(X)
labels = kmeans.predict(X)

# Visualize clusters
plt.scatter(df['popularity'], df['danceability'], c = labels)
plt.xlabel('popularity')
plt.ylabel('danceability')
plt.show()
```

Implementation at [5-Clustering/2-K-Means/README.md:185-196]()

Sources: [5-Clustering/2-K-Means/README.md:142-196]()

## Model Evaluation Techniques

### Silhouette Score

The silhouette score measures cluster separation quality on a scale from -1 to 1:

- **1**: Dense, well-separated clusters
- **0**: Overlapping clusters with samples near decision boundaries
- **-1**: Incorrectly assigned samples

```python
from sklearn import metrics
score = metrics.silhouette_score(X, y_cluster_kmeans)
```

The Nigerian music dataset achieves a silhouette score of **0.53**, indicating moderately formed clusters with data not particularly well-suited to this clustering approach.

Sources: [5-Clustering/2-K-Means/README.md:123-135]()

### Elbow Method

The elbow method determines optimal k by plotting WCSS (within-cluster sum of squares) against cluster count. The "elbow" point where the rate of decrease sharply changes indicates the optimal k value.

```mermaid
graph LR
    subgraph "Elbow Method Process"
        RANGE["Iterate k=1 to 10"]
        TRAIN["Train KMeans<br/>for each k"]
        WCSS["Collect inertia_<br/>WCSS values"]
        PLOT["Plot WCSS vs k<br/>sns.lineplot()"]
        ELBOW["Identify elbow<br/>Optimal k=3"]
    end
    
    RANGE --> TRAIN
    TRAIN --> WCSS
    WCSS --> PLOT
    PLOT --> ELBOW
    
    subgraph "Metrics"
        INERTIA["inertia_<br/>Sum squared distances"]
        AVG["Average distance<br/>to centroid"]
        MIN["Minimize inertia<br/>Internal coherence"]
    end
    
    WCSS --> INERTIA
    INERTIA --> AVG
    AVG --> MIN
```

For the Nigerian music dataset, the elbow method confirms k=3 as optimal, matching the three genre categories in the filtered data.

Sources: [5-Clustering/2-K-Means/README.md:164-182]()

### Model Accuracy Assessment

```python
labels = kmeans.labels_
correct_labels = sum(y == labels)
print("Result: %d out of %d samples were correctly labeled." % (correct_labels, y.size))
print('Accuracy score: {0:0.2f}'. format(correct_labels/float(y.size)))
```

The model exhibits low accuracy due to data characteristics:

**Problem Indicators:**
- **Imbalanced data**: Unequal feature ranges
- **Low correlation**: Insufficient relationship between features
- **High variance**: Column values diverge significantly from mean
- **Skewed clusters**: Heavily influenced by pre-defined genre categories

Sources: [5-Clustering/2-K-Means/README.md:198-220]()

### Variance Problem

Variance measures "average of squared differences from the mean." In clustering context, high variance indicates dataset numbers diverge too much from the mean, causing poor cluster formation.

**Remediation Strategies:**
1. **Data scaling**: Normalize features to similar ranges
2. **Feature selection**: Test different column combinations
3. **Algorithm selection**: Try alternative clustering methods
4. **Weighting**: Apply weights to emphasize certain features

The curriculum notes that standard scaling can smooth the elbow graph but may reduce silhouette score, as unscaled data allows features with less variance to carry more weight.

Sources: [5-Clustering/2-K-Means/README.md:221-236]()

## Data Processing Pipeline

### Complete Workflow

```mermaid
graph TB
    subgraph "Input"
        RAW["nigerian-songs.csv<br/>530 songs, 16 features"]
    end
    
    subgraph "Load and Inspect"
        LOAD["pd.read_csv()"]
        HEAD["df.head()<br/>Preview data"]
        INFO["df.info()<br/>530 non-null entries"]
        NULL_CHK["df.isnull().sum()<br/>Verify 0 nulls"]
    end
    
    subgraph "Clean and Filter"
        STATS["df.describe()<br/>Statistical summary"]
        GENRE_CNT["value_counts()<br/>Top genres"]
        FILT_MISS["Remove 'Missing' genre"]
        FILT_TOP["Keep top 3 genres:<br/>afro dancehall, afropop<br/>nigerian pop"]
        FILT_POP["popularity > 0<br/>Remove unranked"]
    end
    
    subgraph "Feature Engineering"
        SELECT["Select columns:<br/>artist_top_genre<br/>popularity, danceability<br/>acousticness, loudness, energy"]
        ENCODE["LabelEncoder<br/>fit_transform()"]
        SPLIT["X = features<br/>y = encoded_genre"]
    end
    
    subgraph "Visualization"
        BOX_VIZ["Boxplots<br/>Detect outliers"]
        CORR_VIZ["Correlation heatmap<br/>Feature relationships"]
        DIST_VIZ["KDE jointplot<br/>Distribution analysis"]
    end
    
    subgraph "Model Training"
        ELBOW_CALC["Elbow method<br/>Determine k"]
        KMEANS_TRAIN["KMeans(n_clusters=3)<br/>fit(X)"]
        PREDICT["predict(X)<br/>Cluster assignments"]
    end
    
    subgraph "Evaluation"
        SIL_CALC["silhouette_score(X, labels)<br/>Quality metric"]
        ACC_CALC["Accuracy calculation<br/>Compare y and labels"]
        SCATTER["Scatter plot<br/>Visualize clusters"]
    end
    
    RAW --> LOAD
    LOAD --> HEAD
    HEAD --> INFO
    INFO --> NULL_CHK
    NULL_CHK --> STATS
    STATS --> GENRE_CNT
    GENRE_CNT --> FILT_MISS
    FILT_MISS --> FILT_TOP
    FILT_TOP --> FILT_POP
    FILT_POP --> SELECT
    SELECT --> ENCODE
    ENCODE --> SPLIT
    SPLIT --> BOX_VIZ
    SPLIT --> CORR_VIZ
    SPLIT --> DIST_VIZ
    BOX_VIZ --> ELBOW_CALC
    ELBOW_VIZ --> ELBOW_CALC
    ELBOW_CALC --> KMEANS_TRAIN
    KMEANS_TRAIN --> PREDICT
    PREDICT --> SIL_CALC
    PREDICT --> ACC_CALC
    PREDICT --> SCATTER
```

Sources: [5-Clustering/1-Visualize/README.md:100-314](), [5-Clustering/2-K-Means/README.md:35-236]()

## Key Implementation Files

| File Path | Purpose | Key Components |
|-----------|---------|----------------|
| `5-Clustering/1-Visualize/README.md` | Clustering introduction | Algorithm taxonomy, use cases, dataset exploration |
| `5-Clustering/2-K-Means/README.md` | K-Means implementation | Algorithm mechanics, elbow method, silhouette scoring |
| `5-Clustering/1-Visualize/notebook.ipynb` | Visualization exercises | Seaborn plots, correlation analysis, KDE plots |
| `5-Clustering/2-K-Means/notebook.ipynb` | K-Means training | Model training loop, WCSS calculation, cluster visualization |
| `5-Clustering/data/nigerian-songs.csv` | Dataset | 530 songs with audio features |

Sources: [5-Clustering/1-Visualize/README.md:104](), [5-Clustering/2-K-Means/README.md:35]()

## Integration with Other Modules

The unsupervised learning module builds on foundational concepts from earlier modules while contrasting with supervised approaches:

**Prerequisites:**
- Data manipulation with pandas (from [Core ML Concepts](#2))
- Visualization with matplotlib/seaborn
- Scikit-learn model APIs

**Contrasts with Supervised Learning:**
- No labeled training data required
- Discovers inherent patterns vs. learning from examples
- Uses distance metrics vs. prediction error minimization
- Cluster IDs vs. class predictions

**Leads to:**
- Feature understanding for supervised models
- Dimensionality reduction techniques
- Anomaly detection applications in real-world scenarios

Sources: [5-Clustering/1-Visualize/README.md:1-32]()

---

