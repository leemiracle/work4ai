<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ML-For-Beginners · extra page RL Model Deployment with Flask · fetched 2026-10-26 -->

# RL Model Deployment with Flask

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [3-Web-App/1-Web-App/README.md](3-Web-App/1-Web-App/README.md)
- [8-Reinforcement/1-QLearning/README.md](8-Reinforcement/1-QLearning/README.md)
- [8-Reinforcement/1-QLearning/assignment.md](8-Reinforcement/1-QLearning/assignment.md)
- [8-Reinforcement/1-QLearning/notebook.ipynb](8-Reinforcement/1-QLearning/notebook.ipynb)
- [8-Reinforcement/1-QLearning/rlboard.py](8-Reinforcement/1-QLearning/rlboard.py)
- [8-Reinforcement/1-QLearning/solution/assignment-solution.ipynb](8-Reinforcement/1-QLearning/solution/assignment-solution.ipynb)
- [8-Reinforcement/1-QLearning/solution/notebook.ipynb](8-Reinforcement/1-QLearning/solution/notebook.ipynb)
- [8-Reinforcement/1-QLearning/solution/rlboard.py](8-Reinforcement/1-QLearning/solution/rlboard.py)
- [8-Reinforcement/2-Gym/README.md](8-Reinforcement/2-Gym/README.md)
- [8-Reinforcement/2-Gym/assignment.md](8-Reinforcement/2-Gym/assignment.md)
- [8-Reinforcement/2-Gym/images/escape.png](8-Reinforcement/2-Gym/images/escape.png)
- [8-Reinforcement/2-Gym/notebook.ipynb](8-Reinforcement/2-Gym/notebook.ipynb)
- [8-Reinforcement/2-Gym/solution/notebook.ipynb](8-Reinforcement/2-Gym/solution/notebook.ipynb)
- [8-Reinforcement/README.md](8-Reinforcement/README.md)
- [8-Reinforcement/images/peter.png](8-Reinforcement/images/peter.png)

</details>



## Purpose and Scope

This document describes the process of deploying trained Reinforcement Learning models using Flask web applications. It covers model persistence techniques for Q-Learning algorithms, Flask application structure for RL inference, and the workflow for serving trained agents in production environments. This page focuses on deployment mechanics rather than training algorithms.

For RL training fundamentals, see [5.3.1](#5.3.1). For Gym environment usage during training, see [5.3.2](#5.3.2). For general ML model deployment patterns with classification models, see [3.2.3](#3.2.3).

## Model Persistence in Reinforcement Learning

### Q-Table Serialization

Unlike supervised learning models that have explicit `fit()` and `predict()` methods, Q-Learning algorithms store learned policies in Q-Tables—data structures mapping state-action pairs to Q-values. These tables must be serialized for deployment.

**Pickle-based Persistence**

The Python `pickle` module serializes Q-Table data structures for file storage and later retrieval:

```mermaid
graph LR
    QTable["Q-Table Dictionary<br/>{(state,action): value}"]
    PickleFile["model.pkl"]
    LoadedQ["Loaded Q-Table"]
    
    QTable -->|"pickle.dump()"| PickleFile
    PickleFile -->|"pickle.load()"| LoadedQ
```

**Q-Table Structure Types**

Two primary Q-Table implementations appear in the codebase:

1. **Numpy Array Q-Tables**: Fixed-size arrays for discrete, bounded state spaces
2. **Dictionary Q-Tables**: Dynamic structures for unbounded or sparse state spaces

Sources: [8-Reinforcement/1-QLearning/README.md:160-167](), [8-Reinforcement/2-Gym/README.md:176-191]()

### Persistence Workflow

```mermaid
graph TB
    Training["Training Loop<br/>5000+ epochs"]
    QUpdate["Q-Table Updates<br/>Q[(s,a)] = (1-α)Q[(s,a)] + α(r+γmax Q[(s',a')])"]
    SaveQ["Save Q-Table<br/>pickle.dump(Q, file)"]
    
    Training --> QUpdate
    QUpdate --> SaveQ
    
    subgraph "Deployment Environment"
        LoadQ["Load Q-Table<br/>Q = pickle.load(file)"]
        Policy["Policy Function<br/>select action from Q-values"]
        Predict["Generate Predictions"]
    end
    
    SaveQ --> LoadQ
    LoadQ --> Policy
    Policy --> Predict
```

The training phase accumulates Q-values through iterative updates, then serializes the final table. The deployment phase loads this table and uses it for action selection without further updates.

Sources: [8-Reinforcement/1-QLearning/README.md:231-257](), [8-Reinforcement/2-Gym/README.md:338-370]()

## Flask Application Architecture for RL Models

### Application Structure

Flask applications for RL deployment follow a standard structure adapted from supervised learning patterns:

```mermaid
graph TB
    subgraph "Project Directory"
        AppPy["app.py<br/>Flask application<br/>route definitions"]
        ModelFile["rl-model.pkl<br/>Pickled Q-Table"]
        
        subgraph "templates/"
            IndexHTML["index.html<br/>User interface<br/>form submission"]
        end
        
        subgraph "static/css/"
            StylesCSS["styles.css<br/>UI styling"]
        end
    end
    
    AppPy -.->|"loads"| ModelFile
    AppPy -.->|"renders"| IndexHTML
    IndexHTML -.->|"links"| StylesCSS
```

Sources: [3-Web-App/1-Web-App/README.md:160-173]()

### Core Flask Components

**app.py Route Structure**

```mermaid
graph TB
    FlaskApp["Flask(__name__)"]
    
    HomeRoute["@app.route('/')<br/>home()<br/>renders index.html"]
    PredictRoute["@app.route('/predict')<br/>methods=['POST']<br/>predict()<br/>processes form data"]
    
    LoadModel["Model Loading<br/>Q = pickle.load('rl-model.pkl')"]
    ActionSelection["Action Selection<br/>action = np.argmax(Q[state])"]
    
    FlaskApp --> HomeRoute
    FlaskApp --> PredictRoute
    
    PredictRoute --> ActionSelection
    LoadModel --> ActionSelection
```

The Flask application defines two primary routes: a root route serving the UI and a prediction route processing inference requests.

Sources: [3-Web-App/1-Web-App/README.md:275-310]()

### Model Loading Pattern

The model loading occurs at application startup, outside request handlers to avoid repeated file I/O:

```mermaid
sequenceDiagram
    participant App as app.py
    participant FS as File System
    participant Pickle as pickle module
    participant Memory as Q-Table in Memory
    
    App->>FS: open('rl-model.pkl', 'rb')
    FS->>Pickle: file handle
    Pickle->>Memory: Q = pickle.load(file)
    Note over Memory: Q-Table ready for inference
    
    loop For each request
        App->>Memory: Access Q[state]
        Memory->>App: Q-values for actions
    end
```

Sources: [3-Web-App/1-Web-App/README.md:277-284]()

## State Preprocessing and Action Selection

### State Discretization

Continuous state spaces from RL environments must be discretized before Q-Table lookup. The codebase implements discretization functions that map continuous observations to discrete states:

```mermaid
graph LR
    ContinuousObs["Continuous Observation<br/>[pos, vel, angle, rot]"]
    Discretize["discretize(obs)<br/>tuple of integers"]
    DiscreteState["Discrete State<br/>(x, y, z, w)"]
    QTable["Q-Table Lookup<br/>Q[(state, action)]"]
    
    ContinuousObs --> Discretize
    Discretize --> DiscreteState
    DiscreteState --> QTable
```

**Discretization Implementation Types**

1. **Linear scaling**: Divide by fixed intervals and convert to integers
2. **Binning**: Use `np.digitize()` with predefined bin edges

Sources: [8-Reinforcement/2-Gym/README.md:122-156]()

### Action Selection Strategies

Two primary action selection strategies for deployment:

```mermaid
graph TB
    State["Discretized State s"]
    GetQValues["qvalues(s)<br/>returns [Q(s,a₀), Q(s,a₁), ...]"]
    
    subgraph "Strategy 1: Argmax"
        Argmax["action = np.argmax(Q[s])"]
        BestAction["Deterministic best action"]
    end
    
    subgraph "Strategy 2: Probabilistic"
        Probs["probs(Q[s])<br/>normalize to probabilities"]
        Sample["random.choices(actions, weights=v)"]
        SampledAction["Stochastic action"]
    end
    
    State --> GetQValues
    GetQValues --> Argmax
    GetQValues --> Probs
    Argmax --> BestAction
    Probs --> Sample
    Sample --> SampledAction
```

The deterministic argmax strategy always selects the highest Q-value action. The probabilistic strategy samples according to Q-value proportions, allowing exploration in production.

Sources: [8-Reinforcement/1-QLearning/README.md:265-275](), [8-Reinforcement/2-Gym/README.md:306-318]()

## Complete Deployment Workflow

### End-to-End Deployment Pipeline

```mermaid
graph TB
    subgraph "Training Phase"
        Env["Environment Setup<br/>Board or Gym"]
        Train["Q-Learning Training<br/>100k epochs"]
        QFinal["Final Q-Table<br/>Dictionary or Array"]
        Save["pickle.dump(Q, file)"]
    end
    
    subgraph "Deployment Phase"
        InstallDeps["Install Dependencies<br/>requirements.txt<br/>Flask, numpy, pickle"]
        CreateApp["Create app.py<br/>Define routes<br/>Load model"]
        CreateUI["Create templates/<br/>index.html<br/>User input form"]
        RunFlask["flask run<br/>or python app.py"]
    end
    
    subgraph "Inference Runtime"
        UserInput["User submits state<br/>via HTML form"]
        ProcessState["Discretize state<br/>Lookup Q-Table"]
        SelectAction["Select action<br/>argmax or sample"]
        ReturnResult["Return action<br/>to user interface"]
    end
    
    Env --> Train
    Train --> QFinal
    QFinal --> Save
    
    Save --> InstallDeps
    InstallDeps --> CreateApp
    CreateApp --> CreateUI
    CreateUI --> RunFlask
    
    RunFlask --> UserInput
    UserInput --> ProcessState
    ProcessState --> SelectAction
    SelectAction --> ReturnResult
```

Sources: [3-Web-App/1-Web-App/README.md:145-314](), [8-Reinforcement/1-QLearning/README.md:231-257]()

### Flask Request/Response Cycle

```mermaid
sequenceDiagram
    participant Browser
    participant FlaskApp as app.py
    participant QTable as Q-Table (Memory)
    participant Template as index.html
    
    Browser->>FlaskApp: GET /
    FlaskApp->>Template: render_template('index.html')
    Template->>Browser: HTML form
    
    Browser->>FlaskApp: POST /predict<br/>state parameters
    FlaskApp->>FlaskApp: Extract form values<br/>discretize state
    FlaskApp->>QTable: Q.get((state, action))
    QTable->>FlaskApp: Q-values array
    FlaskApp->>FlaskApp: Select best action
    FlaskApp->>Template: render with result
    Template->>Browser: Display recommended action
```

Sources: [3-Web-App/1-Web-App/README.md:287-306]()

## Code Entity Mapping

### Key Python Modules and Functions

```mermaid
graph TB
    subgraph "app.py Components"
        FlaskInit["app = Flask(__name__)"]
        PickleLoad["Q = pickle.load(open('model.pkl', 'rb'))"]
        HomeFunc["@app.route('/')<br/>def home():<br/>return render_template('index.html')"]
        PredictFunc["@app.route('/predict', methods=['POST'])<br/>def predict():<br/>process state, return action"]
        RunMain["if __name__ == '__main__':<br/>app.run(debug=True)"]
    end
    
    subgraph "Helper Functions"
        Discretize["def discretize(x):<br/>tuple((x/intervals).astype(int))"]
        QValues["def qvalues(state):<br/>[Q.get((state,a), 0) for a in actions]"]
        Probs["def probs(v):<br/>normalize Q-values to probabilities"]
    end
    
    subgraph "Data Structures"
        QDict["Q = {}<br/>Dictionary Q-Table<br/>{(state, action): value}"]
        QArray["Q = np.ones((w,h,len(actions)))<br/>Array Q-Table"]
        Actions["actions = (0, 1)<br/>or {U, D, L, R}"]
    end
    
    PickleLoad --> QDict
    PickleLoad --> QArray
    PredictFunc --> Discretize
    PredictFunc --> QValues
    QValues --> QDict
    QValues --> Actions
```

**Module Dependencies**

| Module | Purpose | Usage Location |
|--------|---------|----------------|
| `pickle` | Q-Table serialization | Model save/load operations |
| `numpy` | Q-Table arrays, argmax | Action selection, discretization |
| `flask` | Web framework | App initialization, routing |
| `random` | Probabilistic action selection | Exploration during inference |

Sources: [3-Web-App/1-Web-App/README.md:277-310](), [8-Reinforcement/2-Gym/README.md:182-191]()

### Q-Table Data Structure Variants

```mermaid
graph LR
    subgraph "Dictionary Q-Table"
        DictQ["Q = {}<br/>Sparse storage"]
        DictGet["Q.get((state, action), default=0)"]
        DictSet["Q[(state, action)] = value"]
    end
    
    subgraph "Array Q-Table"
        ArrayQ["Q = np.ones((width, height, n_actions))"]
        ArrayGet["Q[x, y, action_idx]"]
        ArraySet["Q[x, y, action_idx] = value"]
    end
    
    subgraph "Use Cases"
        Unbounded["Unbounded state space<br/>Continuous environments"]
        Bounded["Bounded state space<br/>Grid worlds"]
    end
    
    Unbounded -.->|"best for"| DictQ
    Bounded -.->|"best for"| ArrayQ
```

Dictionary Q-Tables handle sparse or unbounded state spaces dynamically. Array Q-Tables provide faster lookup for fixed-size discrete state spaces but require predefined dimensions.

Sources: [8-Reinforcement/1-QLearning/README.md:160-167](), [8-Reinforcement/2-Gym/README.md:176-191]()

## RL vs. Supervised Learning Deployment

### Key Architectural Differences

```mermaid
graph TB
    subgraph "Supervised Learning Deployment"
        SLModel["Trained Model<br/>model.fit(X, y)"]
        SLPickle["model.pkl<br/>scikit-learn object"]
        SLPredict["model.predict(X_new)<br/>Direct prediction"]
    end
    
    subgraph "RL Deployment"
        RLModel["Q-Table<br/>State-action values"]
        RLPickle["rl-model.pkl<br/>Dictionary/Array"]
        RLDiscretize["Discretize state"]
        RLLookup["Q-Table lookup"]
        RLSelect["Action selection<br/>argmax or sample"]
    end
    
    SLModel --> SLPickle
    SLPickle --> SLPredict
    
    RLModel --> RLPickle
    RLPickle --> RLDiscretize
    RLDiscretize --> RLLookup
    RLLookup --> RLSelect
```

**Comparison Table**

| Aspect | Supervised Learning | Reinforcement Learning |
|--------|-------------------|----------------------|
| **Persisted Artifact** | Trained model object with methods | Q-Table data structure |
| **Input Processing** | Feature scaling, encoding | State discretization |
| **Inference Operation** | `model.predict(features)` | Q-Table lookup + action selection |
| **Output Type** | Continuous value or class label | Discrete action |
| **Exploration** | Not applicable | Can sample probabilistically |

Sources: [3-Web-App/1-Web-App/README.md:123-135](), [8-Reinforcement/2-Gym/README.md:304-332]()

### State Representation Requirements

RL models require explicit state discretization for Q-Table-based approaches, while supervised learning models often handle continuous features directly:

```mermaid
graph LR
    subgraph "Supervised Learning"
        SLInput["Raw Features<br/>[x₁, x₂, ..., xₙ]"]
        SLScale["Optional: StandardScaler"]
        SLModel["Model<br/>handles continuous input"]
    end
    
    subgraph "Reinforcement Learning"
        RLObs["Environment Observation<br/>[pos, vel, angle, rot]"]
        RLDiscrete["Required: discretize()<br/>Map to discrete state"]
        RLQTable["Q-Table<br/>requires discrete keys"]
    end
    
    SLInput --> SLScale
    SLScale --> SLModel
    
    RLObs --> RLDiscrete
    RLDiscrete --> RLQTable
```

Sources: [8-Reinforcement/2-Gym/README.md:122-156](), [3-Web-App/1-Web-App/README.md:110-121]()

## Dependencies and Requirements

### Python Package Requirements

```mermaid
graph TB
    ReqFile["requirements.txt"]
    
    Flask["flask<br/>Web framework"]
    Numpy["numpy<br/>Array operations"]
    Pickle["pickle<br/>Standard library"]
    
    Optional["Optional:<br/>gym, matplotlib<br/>(testing only)"]
    
    ReqFile --> Flask
    ReqFile --> Numpy
    Pickle -.->|"Built-in"| ReqFile
    Optional -.->|"Not for production"| ReqFile
```

The `requirements.txt` file should specify Flask and numpy as minimum dependencies. The pickle module is part of Python's standard library and requires no installation.

Sources: [3-Web-App/1-Web-App/README.md:175-183]()

### Installation and Execution Commands

| Command | Purpose |
|---------|---------|
| `pip install -r requirements.txt` | Install dependencies |
| `python app.py` | Run Flask in development mode |
| `flask run` | Alternative Flask execution |
| `export FLASK_DEBUG=1` | Enable debug mode (development only) |

Sources: [3-Web-App/1-Web-App/README.md:184-194](), [3-Web-App/1-Web-App/README.md:309-314]()

---

