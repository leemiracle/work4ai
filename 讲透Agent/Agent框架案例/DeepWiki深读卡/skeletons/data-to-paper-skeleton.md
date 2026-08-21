# Skeleton: data-to-paper（23 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 10KB | 5 | ~5 | 6 |
| 2 | Installation and Setup | L318 | 9KB | 3 | ~2 | 6 |
| 3 | Architecture Overview | L674 | 11KB | 8 | ~5 | 3 |
| 4 | Code Execution System | L1059 | 13KB | 8 | ~2 | 3 |
| 5 | CodeRunner | L1413 | 10KB | 3 | ~4 | 3 |
| 6 | Debugging System | L1731 | 8KB | 4 | ~2 | 3 |
| 7 | Statistical Package Overrides | L1997 | 11KB | 3 | ~2 | 2 |
| 8 | DataFrame Tracking | L2281 | 11KB | 4 | ~1 | 1 |
| 9 | Data Analysis System | L2646 | 9KB | 8 | ~2 | 3 |
| 10 | DataFrame Validation | L2929 | 11KB | 8 | ~5 | 3 |
| 11 | Data Visualization | L3245 | 7KB | 4 | ~4 | 2 |
| 12 | DataFrame Storage and Formatting | L3464 | 10KB | 4 | ~0 | 6 |
| 13 | Document Generation System | L3742 | 10KB | 6 | ~2 | 2 |
| 14 | LaTeX Generation | L4010 | 12KB | 3 | ~0 | 8 |
| 15 | Figure Generation | L4364 | 8KB | 6 | ~3 | 2 |
| 16 | PDF Compilation | L4615 | 7KB | 5 | ~0 | 2 |
| 17 | LLM Interaction System | L4826 | 11KB | 6 | ~5 | 6 |
| 18 | Conversation Management | L5187 | 12KB | 5 | ~11 | 6 |
| 19 | Data Type Extraction | L5544 | 12KB | 9 | ~0 | 7 |
| 20 | External API Integration | L5887 | 10KB | 5 | ~1 | 3 |
| 21 | User Interface | L6149 | 7KB | 6 | ~4 | 1 |
| 22 | PySide App | L6367 | 7KB | 5 | ~3 | 1 |
| 23 | Text Formatting Utilities | L6561 | 6KB | 4 | ~4 | 2 |


## · Overview  (L6)
  源文件: .gitignore, INSTALL.md, MANIFEST.in, README.md, pyproject.toml, release.py
  Purpose and Scope
  High-Level Architecture
    · Core System Components
    · Key Components
  Research Workflow
  Code Execution Environment
  Statistical Override System
  Document Generation System
  Installation and Usage
    · Installation
    · Example Usage
  Key Features
  Package Components
  Next Steps

## · Installation and Setup  (L318)
  源文件: .gitignore, INSTALL.md, MANIFEST.in, README.md, pyproject.toml, release.py
  Overview of Installation Process
  System Requirements
    · Supported Platforms
    · Python Requirements
    · Third-Party Software Dependencies
  Installation for Regular Users
  Installation for Developers
  Dependencies
    · Package Dependencies
    · Pandoc Installation
    · LaTeX Installation
  API Key Configuration
    · Required API Keys
    · Setting Up API Keys
    · Obtaining API Keys
  Verification and Testing
    · Running the Application
  Sample Projects
  Troubleshooting
    · Common Issues
    · Getting Help

## · Architecture Overview  (L674)
  源文件: INSTALL.md, README.md, tests/functional/latex/test_process_latex.py
  Purpose and Scope
  High-Level System Architecture
  Core Components
    · 1. Code Execution System
    · 2. Statistical Override System
    · 3. Data Analysis System
    · 4. Document Generation System
    · 5. Conversation Management System
    · 6. User Interface System
  Data and Control Flow
  Security and Validation Features

## · Code Execution System  (L1059)
  源文件: tests/functional/base_steps/test_debugger.py, tests/functional/base_steps/test_request_code.py, tests/functional/run_gpt_code/test_run_code.py
  System Architecture
  Core Components
    · CodeRunner
    · Security Mechanisms
    · Error Handling and Debugging
  Statistical Package Overrides
  DataFrame Tracking
  Output File Requirements
  Integration with Other Systems
  Usage Examples

## · CodeRunner  (L1413)
  源文件: tests/functional/base_steps/test_debugger.py, tests/functional/base_steps/test_request_code.py, tests/functional/run_gpt_code/test_run_code.py
  Overview
  Architecture and Components
    · CodeRunner Core Architecture
    · Integration with Data-to-Paper Framework
  Key Features
    · Code Execution
    · Security Restrictions
    · Error Handling
    · Warning Management
    · Output File Requirements
  Extension and Customization
    · Custom Run Contexts
    · Custom CodeRunner Subclasses
  Usage Examples
    · Basic Code Execution
    · Executing Code with Statistical Overrides
    · Reproducible Machine Learning
  Integration with Debugging System
  Summary

## · Debugging System  (L1731)
  源文件: tests/functional/base_steps/test_debugger.py, tests/functional/base_steps/test_request_code.py, tests/functional/run_gpt_code/test_run_code.py
  Components and Architecture
  Debugging Workflow
    · Key Methods
  Error Types and Handling
    · 1. Syntax Errors
    · 2. Execution Errors
    · 3. Runtime Issues
    · 4. Forgiveness Mechanism
  Integration with Other Systems
    · Integration with Code Generation
    · Integration with Statistical Overrides
  Example Debugging Flow
  Configuration Options
  Timeout Handling

## · Statistical Package Overrides  (L1997)
  源文件: tests/functional/run_gpt_code/test_sklearn.py, tests/functional/run_gpt_code/test_statsmodels.py
  Purpose and Overview
  Architecture Overview
  P-Value Tracking System
  Package-Specific Overrides
    · Statsmodels Overrides
    · Scipy Overrides
    · Scikit-learn Overrides
  Integration with Code Execution System
  Common Issues Detected
  Usage Examples
    · Basic Usage with CodeRunner
    · Manual Context Usage
  Best Practices
  Limitations and Considerations

## · DataFrame Tracking  (L2281)
  源文件: tests/functional/run_gpt_code/test_reporting_dataframe.py
  Purpose and Scope
  Overview
  Core Components
  Using the DataFrame Tracker
  Key Features and Functionality
    · 1. DataFrame Creation Tracking
    · 2. DataFrame Modification Tracking
    · 3. DataFrame Saving Tracking
    · 4. Enforcing Save Requirements
    · 5. Enhanced Error Messages
    · 6. Method Restrictions
    · 7. Output Formatting Control
  Configuration Options
  Integration with Data Analysis Workflow
  Common Usage Patterns
  Conclusion

## · Data Analysis System  (L2646)
  源文件: tests/functional/research_types/scientific_research/test_df_file_formatting.py, tests/functional/run_gpt_code/test_mydata_df.py, tests/functional/utils/test_check_types.py
  System Architecture
  Key Components
    · InfoDataFrame
    · Data Validation System
    · Data Transformation
    · Statistical Processing
  DataFrame Tracking
  Integration with Other Systems
  Data View Purposes
  Data Flow

## · DataFrame Validation  (L2929)
  源文件: tests/functional/research_types/scientific_research/test_df_file_formatting.py, tests/functional/run_gpt_code/test_mydata_df.py, tests/functional/utils/test_check_types.py
  Purpose and Scope
  DataFrame Validation Architecture
  InfoDataFrame: The Foundation for Validation
  Type Validation
    · Core Type Validation Functions
  DataFrame Content Requirements
    · Analysis DataFrame Requirements
    · Display Item DataFrame Requirements
  View Purpose and Presentation Context
    · ViewPurpose Options
  Special Value Handling
    · P-Value Handling
  DataFrame Validation Integration
  Handling Special Cases
    · Special Character Handling
  Summary

## · Data Visualization  (L3245)
  源文件: tests/functional/graphics/test_create_figure.py, tests/functional/graphics/test_df_to_figure.py
  Purpose and Scope
  System Overview
  Core Functions
  Visualization Features
    · Core Plotting Capabilities
    · Visualization Types and Options
  Document Integration Features
    · LaTeX Output Customization
  Usage Examples
    · Basic Plot
    · Plot with Error Bars and P-values
    · Multiple Series with Confidence Intervals
  Key Implementation Details
    · Figure Generation
    · Validation Rules
  Integration with the Document Generation System

## · DataFrame Storage and Formatting  (L3464)
  源文件: tests/functional/latex/test_tables.py, tests/functional/research_types/scientific_research/test_df_file_formatting.py, tests/functional/research_types/scientific_research/test_utils_modified_for_gpt_use.py, tests/functional/run_gpt_code/test_mydata_df.py, tests/functional/utils/test_check_types.py, tests/functional/utils/test_dataframe.py
  Purpose and Overview
  InfoDataFrame Class
    · InfoDataFrame Class Hierarchy
  DataFrame Serialization
    · DataFrame Serialization Flow
  DataFrame Formatting for Different Views
    · DataFrame View Formatting System
  Conversion to Presentation Formats
    · DataFrame Presentation Conversion System
  LaTeX Integration
  Special Data Type Handling
  Integration with Document Generation
  Type Validation

## · Document Generation System  (L3742)
  源文件: tests/functional/latex/test_latex_to_pdf.py, tests/functional/research_types/scientific_research/test_df_check.py
  System Overview
  Key Components and Workflow
  DataFrame Validation
  LaTeX Generation
    · DataFrame to LaTeX Workflow
  Figure Generation
    · Figure Generation Configuration
  PDF Compilation
    · LaTeX Compilation Process
    · LaTeX Expression Evaluation
  Citation Management
  Error Handling
  Integration with Other Systems

## · LaTeX Generation  (L4010)
  源文件: tests/functional/base_steps/test_request_latex.py, tests/functional/base_steps/test_request_multi_choice.py, tests/functional/base_steps/test_request_python_value.py, tests/functional/base_steps/test_request_quoted_text.py, tests/functional/base_steps/test_review_dialog.py, tests/functional/base_steps/utils.py, tests/functional/latex/test_latex_to_pdf.py, tests/functional/research_types/scientific_research/test_df_check.py
  Purpose and Overview
  System Architecture
    · LaTeX Generation Flow
    · Key Components and Interactions
  Core Components
    · LatexDocument Class
    · LaTeX to PDF Conversion
    · LaTeX Text Processing
    · LaTeX Mathematical Expression Evaluation
  Citation Handling
    · CrossrefCitation Class
  DataFrame to LaTeX Conversion
    · Analysis DataFrame to LaTeX
    · Display Items DataFrame to LaTeX
  LLM Interaction for LaTeX Generation
    · LaTeX Review Background Products Converser
  Error Handling and Validation
    · LaTeX Compilation Error Handling
    · LaTeX Content Validation
  Usage Examples
    · Basic LaTeX Compilation
    · Converting DataFrame to LaTeX
    · Requesting LaTeX from LLM

## · Figure Generation  (L4364)
  源文件: tests/functional/graphics/test_create_figure.py, tests/functional/graphics/test_df_to_figure.py
  Purpose and Scope
  Figure Generation Architecture
  Core Components
    · DataFrame to Figure Conversion
  Figure Creation Process
    · Key Parameters
    · Statistical Annotations Support
    · Multiple Series Support
  LaTeX Integration
    · LaTeX Output Example
  Special Handling for Long Labels
  Validation and Requirements
  Integration with Document Generation
  Usage Example

## · PDF Compilation  (L4615)
  源文件: tests/functional/latex/test_latex_to_pdf.py, tests/functional/research_types/scientific_research/test_df_check.py
  PDF Compilation Process Overview
  Key Components
    · `save_latex_and_compile_to_pdf` Function
    · Citation Handling
  Error Handling
  LaTeX Text Processing and Expression Evaluation
    · Processing LaTeX Text
    · LaTeX Expression Evaluation
  Integration with DataFrame Visualization
  LatexDocument Class

## · LLM Interaction System  (L4826)
  源文件: tests/functional/conversation/conftest.py, tests/functional/conversation/test_actions.py, tests/functional/conversation/test_conversation.py, tests/functional/conversation/test_conversation_manager.py, tests/functional/conversation/test_message_designation.py, tests/functional/utils/test_ref_numeric_values.py
  System Architecture
    · Overview Diagram
    · Interaction Flow
  Conversation Management
    · ConversationManager
    · Message Types and Roles
    · Conversation Actions
    · Message Designation
  Data Type Extraction
    · Numeric Value Extraction
  LLM API Integration
    · LLM Response Handling
    · Advanced Integration Features
  Usage Examples
    · Basic Conversation
    · Conversation Management

## · Conversation Management  (L5187)
  源文件: tests/functional/conversation/conftest.py, tests/functional/conversation/test_actions.py, tests/functional/conversation/test_conversation.py, tests/functional/conversation/test_conversation_manager.py, tests/functional/conversation/test_message_designation.py, tests/functional/utils/test_ref_numeric_values.py
  Purpose and Scope
  System Overview
  Core Components
    · Conversation Manager
    · Conversation and Messages
    · Conversation Actions
    · Message Designation
  Integration with Other Systems
  Usage Examples
    · Creating and Managing a Conversation
    · Working with Code Responses
    · Saving and Loading Conversations
  Best Practices

## · Data Type Extraction  (L5544)
  源文件: tests/functional/base_steps/test_request_latex.py, tests/functional/base_steps/test_request_multi_choice.py, tests/functional/base_steps/test_request_python_value.py, tests/functional/base_steps/test_request_quoted_text.py, tests/functional/base_steps/test_review_dialog.py, tests/functional/base_steps/utils.py, tests/functional/utils/test_replacer.py
  Purpose and Scope
  System Architecture
  Data Flow
  Python Value Extraction
    · Key Features
    · Example Flow
    · Specialized Dictionary Extraction
  LaTeX Extraction
    · Key Features
    · Example Flow
    · Citation Handling
  Quoted Text Extraction
    · Key Features
    · Example Flow
  Multiple Choice Extraction
    · Key Features
  Common Functionality
    · Error Handling and Conversation Rewinding
    · Model Strength Adjustment
  Integration with Conversation Management
  Value Formatting and Replacement

## · External API Integration  (L5887)
  源文件: tests/functional/servers/__init__.py, tests/functional/servers/test_api_keys.py, tests/functional/servers/test_servers.py
  Overview
  Architecture
  Server Caller Classes
    · ListServerCaller
    · ParameterizedQueryServerCaller
    · OrderedKeyToListServerCaller
  API Key Management
  Connection Verification
  Mocking System for Testing
    · Key Mocking Features
    · Mocking Methods
  Semantic Scholar Integration
  Error Handling
  Testing Support

## · User Interface  (L6149)
  源文件: tests/functional/interactive/test_pyside_app.py
  Overview of the UI System
  PysideApp Class
    · Key Methods:
  Panel System
  Text Formatting
    · Features of Text Formatting:
  User Interaction Flow
    · Typical Interaction Pattern:
  Application Initialization
  Content Display Capabilities
  Integration with Other Systems

## · PySide App  (L6367)
  源文件: tests/functional/interactive/test_pyside_app.py
  Purpose and Scope
  Architecture and Components
  Initialization and Usage Flow
  Key Functionalities
  Panel System
  Text Formatting Integration
  Application Setup and Integration
  Example Usage
  Conclusion

## · Text Formatting Utilities  (L6561)
  源文件: tests/functional/interactive/test_pyside_app.py, tests/functional/utils/test_check_numeric_values.py
  Purpose and Scope
  Text Formatting with Code Blocks
    · Key Features
    · Usage Example
    · Text Formatting Process
  Numeric Value Utilities
    · Key Components
    · Numeric Value Validation Process
    · Supported Number Formats
  Integration with User Interface
    · UI Integration Flow
  Code Block Type Support
  Numeric Validation Behavior
    · Validation Rules