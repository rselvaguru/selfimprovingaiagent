"""
Configuration file for Self-Improving AI Agent Framework

Author: Selvagurunathan Ramalingam
Date: March 10, 2026
Version: 1.0

Description:
    Central configuration for all framework settings including
    Ollama API, agent parameters, memory configuration, and API settings.
"""

# Ollama Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama2"

# Agent Configuration
EXECUTOR_TEMPERATURE = 0.7
EVALUATOR_TEMPERATURE = 0.3
OPTIMIZER_TEMPERATURE = 0.5

# Learning Loop Configuration
MAX_ITERATIONS = 3
SCORE_THRESHOLD = 8  # Stop when score reaches this threshold

# Memory Configuration
MEMORY_PERSIST_DIR = "./chroma_data"
MEMORY_SIMILARITY_THRESHOLD = 0.7

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "./logs/agent.log"

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_WORKERS = 4

# Batch Processing
BATCH_SIZE = 10
BATCH_TIMEOUT = 300  # 5 minutes
