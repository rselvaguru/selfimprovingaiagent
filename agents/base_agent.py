"""
Base Agent Class - Abstract Interface

Author: Selvagurunathan Ramalingam
Date: March 10, 2026
Version: 1.0

Description:
    Abstract base class for all agents in the Self-Improving AI Agent Framework.
    Defines the interface that all agents must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from utils.logger import Logger


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the Self-Improving AI Agent Framework.
    
    Defines the interface that all agents must implement.
    """
    
    def __init__(self, name: str, model: str = "llama2", temperature: float = 0.7):
        """
        Initialize base agent.
        
        Args:
            name: Agent name
            model: LLM model to use (default: llama2)
            temperature: Temperature for LLM response (default: 0.7)
        """
        self.name = name
        self.model = model
        self.temperature = temperature
        self.logger = Logger(name)
        self.logger.info(f"Initialized {name} agent with model={model}, temperature={temperature}")
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Output data from the agent
        """
        pass
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name={self.name}, model={self.model})"
