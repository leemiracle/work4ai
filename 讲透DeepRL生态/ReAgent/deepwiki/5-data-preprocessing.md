> 来源: [https://deepwiki.com/facebookresearch/ReAgent/5-data-preprocessing](https://deepwiki.com/facebookresearch/ReAgent/5-data-preprocessing)
> DeepWiki facebookresearch/ReAgent | Last indexed: 21 April 2025 (9e707c

# Data Preprocessing

  Relevant source files 
 - [preprocessing/pom.xml](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/pom.xml)
 - [preprocessing/src/main/scala/com/facebook/spark/rl/Constants.scala](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/main/scala/com/facebook/spark/rl/Constants.scala)
 - [preprocessing/src/main/scala/com/facebook/spark/rl/Helper.scala](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/main/scala/com/facebook/spark/rl/Helper.scala)
 - [preprocessing/src/main/scala/com/facebook/spark/rl/MultiStepTimeline.scala](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/main/scala/com/facebook/spark/rl/MultiStepTimeline.scala)
 - [preprocessing/src/main/scala/com/facebook/spark/rl/Timeline.scala](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/main/scala/com/facebook/spark/rl/Timeline.scala)
 - [preprocessing/src/main/scala/com/facebook/spark/rl/Udfs.scala](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/main/scala/com/facebook/spark/rl/Udfs.scala)
 - [preprocessing/src/test/scala/com/facebook/spark/common/testutil/PipelineTester.scala](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/test/scala/com/facebook/spark/common/testutil/PipelineTester.scala)
 - [preprocessing/src/test/scala/com/facebook/spark/common/testutil/TestLogging.scala](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/test/scala/com/facebook/spark/common/testutil/TestLogging.scala)
 - [preprocessing/src/test/scala/com/facebook/spark/rl/TimelineTest.scala](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/test/scala/com/facebook/spark/rl/TimelineTest.scala)
 - [reagent/test/workflow/reagent_sql_test_base.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/workflow/reagent_sql_test_base.py)
 - [reagent/test/workflow/test_oss_workflows.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/workflow/test_oss_workflows.py)
 - [reagent/test/workflow/test_preprocessing.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/workflow/test_preprocessing.py)
 - [reagent/test/workflow/test_query_data.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/workflow/test_query_data.py)
 - [reagent/test/workflow/test_query_data_parametric.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/workflow/test_query_data_parametric.py)
 - [reagent/workflow/gym_batch_rl.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/gym_batch_rl.py)
 - [reagent/workflow/identify_types_flow.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/identify_types_flow.py)
 - [reagent/workflow/utils.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/utils.py)
 
  This page describes the data preprocessing systems in ReAgent, focusing on how raw data from environments or logs is transformed into suitable formats for reinforcement learning models. For information about model input/output formats specifically, see [Model Inputs and Outputs](https://deepwiki.com/facebookresearch/ReAgent/2.2-model-inputs-and-outputs).

 
## Overview

 ReAgent's data preprocessing pipeline handles several critical tasks:

 
 - **Timeline Processing**: Converting sequences of states, actions, and rewards into properly structured transition data
 - **Feature Type Identification**: Determining whether features are continuous, categorical, etc.
 - **Normalization**: Calculating statistics for feature normalization
 - **Data Loading**: Efficiently feeding preprocessed data into training loops
 
 
```

```

 Sources: [preprocessing/src/main/scala/com/facebook/spark/rl/Timeline.scala124-427](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/main/scala/com/facebook/spark/rl/Timeline.scala#L124-L427) [reagent/workflow/identify_types_flow.py25-116](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/identify_types_flow.py#L25-L116) [reagent/workflow/utils.py47-62](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/utils.py#L47-L62)

 
## Timeline Processing

 Timeline processing is a critical first step that converts raw logs of environment interactions into a format suitable for reinforcement learning algorithms. It's implemented as Spark SQL transformations in Scala.

 
### Purpose and Input/Output Format

 The Timeline processor takes tabular data with sequential interactions and converts it into transition data with proper state, action, reward, and next state relationships.

 **Input Table Format:**

 
 - `mdp_id` (STRING): Unique identifier for each episode
 - `sequence_number` (BIGINT): Position within the MDP sequence
 - `state_features` (MAP<BIGINT,DOUBLE>): Current state representation
 - `action` (STRING or MAP<BIGINT,DOUBLE>): Action taken
 - `action_probability` (DOUBLE): Probability that the action was taken
 - `reward` (DOUBLE): Reward received
 - `possible_actions` (ARRAY): Possible actions at this state (optional)
 - Additional metrics columns
 
 **Output Table Format:**

 
 - All input columns
 - `next_state_features`: Features of the next state
 - `next_action`: Action taken at the next state
 - `sequence_number_ordinal`: Normalized sequence number
 - `time_diff`: Steps between current and next state
 - `possible_next_actions`: Possible actions at next state
 
 
```

```

 Sources: [preprocessing/src/main/scala/com/facebook/spark/rl/Timeline.scala30-117](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/main/scala/com/facebook/spark/rl/Timeline.scala#L30-L117) [preprocessing/src/test/scala/com/facebook/spark/rl/TimelineTest.scala14-123](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/test/scala/com/facebook/spark/rl/TimelineTest.scala#L14-L123)

 
### Single-Step vs Multi-Step Timeline

 ReAgent supports two timeline processing approaches:

 
 - **Single-Step Timeline**: Converts each state-action pair to a single transition (state, action, reward, next_state)
 - **Multi-Step Timeline**: Creates transitions that span multiple steps, useful for algorithms that use n-step returns or temporal abstraction
 
 
```

```

 The `MultiStepTimeline` class handles n-step transitions by creating arrays of rewards, next states and next actions.

 Sources: [preprocessing/src/main/scala/com/facebook/spark/rl/Timeline.scala124-427](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/main/scala/com/facebook/spark/rl/Timeline.scala#L124-L427) [preprocessing/src/main/scala/com/facebook/spark/rl/MultiStepTimeline.scala1-324](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/main/scala/com/facebook/spark/rl/MultiStepTimeline.scala#L1-L324) [preprocessing/src/test/scala/com/facebook/spark/rl/TimelineTest.scala127-320](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/test/scala/com/facebook/spark/rl/TimelineTest.scala#L127-L320)

 
### Timeline Configuration

 Timeline processing can be configured with several options:

 
 - `addTerminalStateRow`: Whether to include terminal states
 - `outlierEpisodeLengthPercentile`: Filter out episodes beyond a certain length (percentile)
 - `timeWindowLimit`: Maximum time window to consider for transitions
 - `rewardColumns`: Specifies which columns contain rewards
 - `extraFeatureColumns`: Additional columns to include in timeline
 
 
```

```

 Sources: [preprocessing/src/main/scala/com/facebook/spark/rl/Timeline.scala15-28](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/main/scala/com/facebook/spark/rl/Timeline.scala#L15-L28) [preprocessing/src/main/scala/com/facebook/spark/rl/MultiStepTimeline.scala8-15](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/main/scala/com/facebook/spark/rl/MultiStepTimeline.scala#L8-L15)

 
### Example Usage in Gym Environment Integration

 The timeline operator is used in the `gym_batch_rl.py` to convert data from gym environments into the proper format:

 
```

```

 Sources: [reagent/workflow/gym_batch_rl.py138-164](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/gym_batch_rl.py#L138-L164)

 
## Feature Type Identification and Normalization

 After timeline processing, ReAgent identifies feature types and calculates normalization parameters to standardize the data.

 
### Feature Type Identification

 The `identify_normalization_parameters` function analyzes feature distributions to determine the appropriate processing for each feature:

 
 - **Continuous Features**: Features with many unique values, normalized with mean/stddev
 - **Categorical Features**: Features with limited distinct values, converted to one-hot encoding
 - **Binary Features**: Features with only 0/1 values
 - **Boxed Continuous Features**: Features that need box-cox transformation
 
 
```

```

 Sources: [reagent/workflow/identify_types_flow.py25-87](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/identify_types_flow.py#L25-L87) [reagent/test/workflow/test_preprocessing.py32-72](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/workflow/test_preprocessing.py#L32-L72)

 
### Normalization Parameter Calculation

 For each identified feature, appropriate normalization parameters are calculated based on a sample of values:

 
```

```

 The `identify_normalization_parameters` function:

 
 - Reads the data using Spark SQL
 - Samples feature values using `create_normalization_spec_spark`
 - Processes each feature to determine its type and parameters
 - Returns a dictionary mapping feature IDs to normalization parameters
 
 Sources: [reagent/workflow/identify_types_flow.py90-115](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/identify_types_flow.py#L90-L115) [reagent/test/workflow/test_preprocessing.py55-72](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/workflow/test_preprocessing.py#L55-L72)

 
## Data Loading Pipeline

 ReAgent's data loading pipeline connects preprocessed data to model training.

 
### Petastorm Integration

 ReAgent uses Petastorm to efficiently read parquet files:

 
```

```

 The `get_petastorm_dataloader` function creates a DataLoader that:

 
 - Reads from parquet files using Petastorm
 - Applies a batch preprocessor
 - Optionally transfers data to GPU
 
 Sources: [reagent/workflow/utils.py64-83](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/utils.py#L64-L83)

 
### PyTorch Lightning Integration

 ReAgent integrates with PyTorch Lightning through the `PetastormLightningDataModule`:

 
```

```

 This module:

 
 - Takes train and evaluation datasets
 - Provides dataloader methods for PyTorch Lightning
 - Handles closing Petastorm readers when done
 
 The data module is used in the `train_eval_lightning` function to train models with PyTorch Lightning.

 Sources: [reagent/workflow/utils.py87-118](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/utils.py#L87-L118) [reagent/workflow/utils.py135-177](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/utils.py#L135-L177)

 
## End-to-End Data Processing Flow

 The complete data processing pipeline integrates all components:

 
```

```

 Sources: [reagent/workflow/utils.py135-177](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/utils.py#L135-L177) [reagent/workflow/identify_types_flow.py90-115](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/workflow/identify_types_flow.py#L90-L115)

 
## Testing and Validation

 ReAgent includes several test suites for data preprocessing:

 
 - Timeline processing tests that verify correct transformation of MDP sequences
 - Query data tests that check proper loading of discrete and parametric action data
 - Preprocessing tests that verify correct identification of feature types and normalization parameters
 
 The test code also provides examples of how the preprocessing components are used in practice.

 Sources: [preprocessing/src/test/scala/com/facebook/spark/rl/TimelineTest.scala14-873](https://github.com/facebookresearch/ReAgent/blob/9e707c09/preprocessing/src/test/scala/com/facebook/spark/rl/TimelineTest.scala#L14-L873) [reagent/test/workflow/test_query_data.py25-238](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/workflow/test_query_data.py#L25-L238) [reagent/test/workflow/test_query_data_parametric.py22-300](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/workflow/test_query_data_parametric.py#L22-L300) [reagent/test/workflow/test_preprocessing.py26-76](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/workflow/test_preprocessing.py#L26-L76)
