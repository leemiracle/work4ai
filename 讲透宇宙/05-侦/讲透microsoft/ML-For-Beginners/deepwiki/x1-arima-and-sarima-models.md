<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ML-For-Beginners · extra page ARIMA and SARIMA Models · fetched 2026-10-26 -->

# ARIMA and SARIMA Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [7-TimeSeries/1-Introduction/README.md](7-TimeSeries/1-Introduction/README.md)
- [7-TimeSeries/2-ARIMA/README.md](7-TimeSeries/2-ARIMA/README.md)
- [7-TimeSeries/README.md](7-TimeSeries/README.md)

</details>



## Purpose and Scope

This document explains the implementation and usage of ARIMA (AutoRegressive Integrated Moving Average) and SARIMA (Seasonal ARIMA) models for time series forecasting in the ML-For-Beginners curriculum. These models are specifically designed to handle non-stationary time series data and predict future values based on historical patterns. The implementation uses the `statsmodels` library's `SARIMAX` class to forecast electricity load consumption.

For general time series concepts and data preparation, see [Time Series Data Processing and Evaluation](#5.2.2). For alternative time series approaches, see [Time Series Forecasting](#5.2).

Sources: [7-TimeSeries/2-ARIMA/README.md:1-50]()

## ARIMA Model Components

ARIMA models decompose time series forecasting into three fundamental components, each represented by a parameter:

| Component | Parameter | Description | Purpose |
|-----------|-----------|-------------|---------|
| **AutoRegressive (AR)** | `p` | Number of lag observations | Incorporates past values of the time series into predictions |
| **Integrated (I)** | `d` | Degree of differencing | Applies differencing to remove non-stationarity and trends |
| **Moving Average (MA)** | `q` | Size of moving average window | Uses past forecast errors to improve predictions |

### Stationarity and Differencing

**Stationarity** refers to data whose statistical properties (mean, variance) do not change over time. Non-stationary data exhibits trends or seasonal patterns that must be transformed before ARIMA modeling.

**Differencing** is the process of computing differences between consecutive observations to remove trends and achieve stationarity. The order of differencing is controlled by parameter `d`:
- `d=0`: No differencing (data is stationary)
- `d=1`: First-order differencing (subtracts previous value)
- `d=2`: Second-order differencing (differences the differences)

The implementation applies differencing automatically during model fitting to stabilize the mean of the time series.

Sources: [7-TimeSeries/2-ARIMA/README.md:15-33](), [7-TimeSeries/1-Introduction/README.md:45-51]()

## SARIMA Seasonal Extension

SARIMA extends ARIMA to handle seasonal patterns in data through additional parameters that model seasonal behavior separately from the trend:

| Parameter | Description | Usage |
|-----------|-------------|-------|
| `P` | Seasonal AR order | Number of seasonal lag observations |
| `D` | Seasonal differencing order | Degree of seasonal differencing |
| `Q` | Seasonal MA order | Size of seasonal moving average window |
| `m` | Seasonal period | Number of time steps per seasonal cycle (e.g., 24 for hourly data with daily seasonality) |

For electricity load data with hourly measurements, the seasonal period `m=24` captures daily patterns where consumption repeats every 24 hours.

Sources: [7-TimeSeries/2-ARIMA/README.md:176-183]()

## ARIMA/SARIMA Implementation Workflow

```mermaid
graph TB
    subgraph "Data Preparation"
        RawData["energy.csv<br/>load column"]
        LoadData["load_data()<br/>returns DataFrame"]
        TrainTest["Train/Test Split<br/>train_start_dt, test_start_dt"]
        Scaling["MinMaxScaler<br/>fit_transform()"]
    end
    
    subgraph "Model Configuration"
        OrderParams["order tuple<br/>(p, d, q)"]
        SeasonalParams["seasonal_order tuple<br/>(P, D, Q, m)"]
    end
    
    subgraph "SARIMAX Training"
        SARIMAXClass["SARIMAX(endog, order, seasonal_order)"]
        Fit["model.fit()<br/>returns results"]
        Summary["results.summary()"]
    end
    
    subgraph "Walk-Forward Validation"
        TrainingWindow["training_window = 720<br/>(30 days)"]
        History["history list<br/>sliding window"]
        Loop["for t in range(test_ts.shape[0])"]
        Forecast["model_fit.forecast(steps=HORIZON)"]
        Update["history.append(obs[0])<br/>history.pop(0)"]
    end
    
    subgraph "Evaluation"
        Predictions["predictions list<br/>yhat values"]
        InverseScale["scaler.inverse_transform()"]
        MAPE["mape() function<br/>common.utils"]
    end
    
    RawData --> LoadData
    LoadData --> TrainTest
    TrainTest --> Scaling
    
    OrderParams --> SARIMAXClass
    SeasonalParams --> SARIMAXClass
    Scaling --> SARIMAXClass
    
    SARIMAXClass --> Fit
    Fit --> Summary
    
    Fit --> TrainingWindow
    TrainingWindow --> History
    History --> Loop
    Loop --> Forecast
    Forecast --> Predictions
    Forecast --> Update
    Update --> Loop
    
    Predictions --> InverseScale
    InverseScale --> MAPE
```

Sources: [7-TimeSeries/2-ARIMA/README.md:35-378]()

## SARIMAX Class and Methods

The `statsmodels.tsa.statespace.sarimax.SARIMAX` class provides the complete implementation for ARIMA and SARIMA models. The key interface is structured as follows:

```mermaid
graph LR
    subgraph "SARIMAX Class Interface"
        Constructor["SARIMAX(endog, order, seasonal_order)"]
        FitMethod["fit() method"]
        Results["SARIMAXResults object"]
        ForecastMethod["forecast(steps) method"]
        SummaryMethod["summary() method"]
    end
    
    subgraph "Parameters"
        Endog["endog: array-like<br/>time series data"]
        Order["order: (p, d, q)<br/>ARIMA parameters"]
        SeasonalOrder["seasonal_order: (P, D, Q, m)<br/>seasonal parameters"]
        Steps["steps: int<br/>forecast horizon"]
    end
    
    subgraph "Outputs"
        Predictions["yhat: array<br/>forecasted values"]
        StatsTable["Statistical summary<br/>coefficients, p-values"]
    end
    
    Endog --> Constructor
    Order --> Constructor
    SeasonalOrder --> Constructor
    Constructor --> FitMethod
    FitMethod --> Results
    Results --> ForecastMethod
    Results --> SummaryMethod
    Steps --> ForecastMethod
    ForecastMethod --> Predictions
    SummaryMethod --> StatsTable
```

### Implementation Example

The typical usage pattern instantiates `SARIMAX` with the training data and parameter specifications, then calls `fit()` to train:

[7-TimeSeries/2-ARIMA/README.md:196-204]()

```python
order = (4, 1, 0)
seasonal_order = (1, 1, 0, 24)

model = SARIMAX(endog=train, order=order, seasonal_order=seasonal_order)
results = model.fit()

print(results.summary())
```

Sources: [7-TimeSeries/2-ARIMA/README.md:54-58](), [7-TimeSeries/2-ARIMA/README.md:170-208]()

## Parameter Selection Strategy

Selecting optimal ARIMA parameters is computationally intensive and somewhat subjective. The implementation uses two approaches:

### Manual Parameter Selection

Manual tuning through experimentation and domain knowledge:

| Parameter Set | Values | Rationale |
|---------------|--------|-----------|
| `order` | (4, 1, 0) or (2, 1, 0) | AR component captures 2-4 hours of lag, first-order differencing removes trend, no MA component |
| `seasonal_order` | (1, 1, 0, 24) | Seasonal AR of 1, first-order seasonal differencing, 24-hour period for daily cycles |

[7-TimeSeries/2-ARIMA/README.md:196-204](), [7-TimeSeries/2-ARIMA/README.md:257-260]()

### Automated Parameter Selection

The implementation references the `auto_arima()` function from the `pyramid` library for automated parameter search, though it is not demonstrated in the provided notebooks. This function performs grid search across parameter combinations using information criteria (AIC/BIC) to identify optimal values.

Sources: [7-TimeSeries/2-ARIMA/README.md:184-194]()

## Model Training and Prediction Workflow

```mermaid
graph TB
    subgraph "Data Preparation Phase"
        LoadEnergy["energy = load_data('./data')"]
        FilterTrain["train = energy[start:end]['load']"]
        FilterTest["test = energy[end:]['load']"]
        ScaleTrain["scaler.fit_transform(train)"]
        ScaleTest["scaler.transform(test)"]
    end
    
    subgraph "Initial Model Training"
        DefineOrder["order = (p, d, q)<br/>seasonal_order = (P, D, Q, m)"]
        CreateModel["model = SARIMAX(endog=train, ...)"]
        FitModel["results = model.fit()"]
        ViewSummary["results.summary()"]
    end
    
    subgraph "Prediction Generation"
        SetHorizon["HORIZON = 3<br/>forecast 3 hours ahead"]
        CallForecast["yhat = model_fit.forecast(steps=HORIZON)"]
        StoreResults["predictions.append(yhat)"]
    end
    
    LoadEnergy --> FilterTrain
    LoadEnergy --> FilterTest
    FilterTrain --> ScaleTrain
    FilterTest --> ScaleTest
    
    ScaleTrain --> DefineOrder
    DefineOrder --> CreateModel
    CreateModel --> FitModel
    FitModel --> ViewSummary
    
    FitModel --> SetHorizon
    SetHorizon --> CallForecast
    CallForecast --> StoreResults
```

### Training Data Configuration

The implementation allocates specific time periods for training and testing:

| Dataset | Period | Duration | Purpose |
|---------|--------|----------|---------|
| Training | 2014-11-01 to 2014-12-29 | ~2 months | Model fitting |
| Testing | 2014-12-30 to 2014-12-31 | 2 days | Evaluation |

[7-TimeSeries/2-ARIMA/README.md:88-106]()

### Scaling Transformation

Before training, the implementation applies `MinMaxScaler` to normalize load values to the [0, 1] interval:

[7-TimeSeries/2-ARIMA/README.md:135-149]()

The scaler is fitted on training data and then applied to test data to prevent data leakage.

Sources: [7-TimeSeries/2-ARIMA/README.md:66-208]()

## Walk-Forward Validation

Walk-forward validation provides robust time series model evaluation by simulating real-world prediction scenarios where models are retrained as new data arrives.

### Validation Algorithm

```mermaid
graph TB
    Initialize["Initialize:<br/>training_window = 720<br/>history = train_ts[-720:]<br/>predictions = []"]
    
    LoopStart["for t in range(test_ts.shape[0]):"]
    
    CreateModel["model = SARIMAX(endog=history,<br/>order=order,<br/>seasonal_order=seasonal_order)"]
    
    FitModel["model_fit = model.fit()"]
    
    Forecast["yhat = model_fit.forecast(steps=HORIZON)"]
    
    StorePred["predictions.append(yhat)"]
    
    GetObs["obs = list(test_ts.iloc[t])"]
    
    UpdateHistory["history.append(obs[0])<br/>history.pop(0)"]
    
    CheckEnd{"More test<br/>data?"}
    
    Complete["Return predictions"]
    
    Initialize --> LoopStart
    LoopStart --> CreateModel
    CreateModel --> FitModel
    FitModel --> Forecast
    Forecast --> StorePred
    StorePred --> GetObs
    GetObs --> UpdateHistory
    UpdateHistory --> CheckEnd
    CheckEnd -->|Yes| LoopStart
    CheckEnd -->|No| Complete
```

### Implementation Details

The walk-forward loop maintains a sliding window of 720 hours (30 days) for training:

[7-TimeSeries/2-ARIMA/README.md:247-272]()

Key variables:
- `training_window = 720`: Fixed window size in hours
- `history`: List containing the current training window
- `predictions`: List accumulating forecasted values
- `obs`: Actual observed values from test set

At each iteration:
1. Train SARIMAX model on current `history` window
2. Forecast next `HORIZON` steps
3. Store predictions
4. Append actual observation to `history`
5. Remove oldest observation from `history` to maintain window size

Sources: [7-TimeSeries/2-ARIMA/README.md:210-286]()

## Evaluation with MAPE

Mean Absolute Percentage Error (MAPE) quantifies prediction accuracy as a percentage. The implementation uses a custom `mape()` function from `common.utils`:

[7-TimeSeries/2-ARIMA/README.md:54-58]()

### MAPE Formula

The MAPE calculation follows this formula:

$$MAPE = \frac{100}{n} \sum_{t=1}^{n} \left| \frac{actual_t - predicted_t}{actual_t} \right|$$

[7-TimeSeries/2-ARIMA/README.md:314-318]()

### MAPE Calculation Process

```mermaid
graph LR
    subgraph "Prediction DataFrame Construction"
        PredArray["predictions list<br/>from walk-forward"]
        EvalDF["eval_df = pd.DataFrame(predictions)"]
        Melt["pd.melt()<br/>reshape for analysis"]
    end
    
    subgraph "Inverse Transformation"
        AddActual["eval_df['actual'] = test_ts values"]
        InverseScale["scaler.inverse_transform()<br/>prediction and actual columns"]
    end
    
    subgraph "MAPE Computation"
        APE["APE = abs(prediction - actual) / actual"]
        OneStep["MAPE for h='t+1'<br/>single step forecast"]
        MultiStep["MAPE for all horizons<br/>multi-step forecast"]
    end
    
    PredArray --> EvalDF
    EvalDF --> Melt
    Melt --> AddActual
    AddActual --> InverseScale
    InverseScale --> APE
    APE --> OneStep
    APE --> MultiStep
```

### MAPE Interpretation

[7-TimeSeries/2-ARIMA/README.md:329-346]()

The implementation reports two MAPE values:
- **One-step forecast MAPE**: Accuracy for predicting 1 time step ahead
- **Multi-step forecast MAPE**: Accuracy across all `HORIZON` steps

Lower MAPE indicates better accuracy. In the example:
- One-step MAPE: ~0.56%
- Multi-step MAPE: ~1.15%

A MAPE of 10% means predictions are off by 10% on average, so values below 2% indicate high accuracy.

Sources: [7-TimeSeries/2-ARIMA/README.md:287-346]()

## Model Persistence and Deployment

While not explicitly demonstrated in the ARIMA lesson, the general pattern for persisting trained models uses Python's `pickle` module, as shown in related time series work:

```python
import pickle

# Save model
with open('model.pkl', 'wb') as f:
    pickle.dump(results, f)

# Load model
with open('model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)
```

For web deployment, see [RL Model Deployment with Flask](#5.3.3) which demonstrates the general Flask deployment pattern applicable to time series models.

Sources: [7-TimeSeries/2-ARIMA/README.md:35-378]()

## Data Preparation Requirements

The ARIMA/SARIMA implementation expects specific data structures and preprocessing:

### Input Data Format

| Requirement | Implementation | Code Reference |
|-------------|----------------|----------------|
| **Index** | DatetimeIndex with hourly frequency | `energy.index` |
| **Column** | Single column named 'load' containing values | `energy[['load']]` |
| **No missing values** | Data must be complete or interpolated | Assumed in preprocessing |
| **Numeric type** | Float64 after scaling | `scaler.fit_transform()` result |

[7-TimeSeries/2-ARIMA/README.md:66-72]()

### Time Series Splitting

Unlike random train/test splits in other ML tasks, time series requires **temporal splitting** to prevent future data leakage:

[7-TimeSeries/2-ARIMA/README.md:84-110]()

The split maintains chronological order: all training data comes before all test data.

Sources: [7-TimeSeries/2-ARIMA/README.md:66-165]()

## Common Parameter Configurations

Based on the electricity load forecasting implementation, typical parameter choices are:

### Conservative Configuration
```python
order = (2, 1, 0)
seasonal_order = (1, 1, 0, 24)
```
- Minimal AR lag (p=2)
- Single differencing (d=1)
- No MA component (q=0)
- Light seasonal AR (P=1)
- 24-hour seasonal period

### Extended Configuration
```python
order = (4, 1, 0)
seasonal_order = (1, 1, 0, 24)
```
- Extended AR lag (p=4) for more historical context
- Same differencing and seasonal structure

[7-TimeSeries/2-ARIMA/README.md:196-204](), [7-TimeSeries/2-ARIMA/README.md:257-260]()

The choice between configurations involves trade-offs:
- Higher `p` captures more historical dependencies but increases computation
- Higher `P` models stronger seasonal effects but may overfit
- Higher `d` or `D` removes more trend/seasonality but may over-difference

Sources: [7-TimeSeries/2-ARIMA/README.md:170-272]()

---

