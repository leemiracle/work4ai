# 环境变量配置

## 开发环境
ENVIRONMENT=development

## 数据库配置
DATABASE_URL=sqlite:///./data/database.db
KNOWLEDGE_BASE_URL=https://knowledge.base

## AI配置
ENABLE_AI=true
AI_MODEL=ollama/llama2
EMBEDDING_MODEL=ollama/deepseek

## 向量数据库
VECTOR_STORE_PATH=./data/chroma
COLLECTION_NAME=learning

## OLLAMA配置
OLLAMA_BASE_URL=http://localhost:11434

## 文档根路径
DOCS_ROOT=./knowledge-base


## 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/platform.log
LOG_FORMAT=%(asctime)s: %(message)s
LOG_LEVEL_CONSOLE=INFO
LOG_FILE_DEBUG=./logs/platform-debug.log


## 应用配置
APP_NAME=IT Learning Platform
APP_VERSION=1.0.0
APP_PORT=3000
DEBUG=false

## 构建配置
BUILD_TYPE=Debug
RUNTIMEOUT=true
