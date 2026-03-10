"""
Executor Agent - Task Execution Component

Author: Selvagurunathan Ramalingam
Date: March 10, 2026
Version: 1.0

Description:
    Agent responsible for executing tasks using the Ollama API.
    Takes a user task and sends it to the local LLM to generate a response.
"""

import requests
import json
from typing import Any, Dict
from agents.base_agent import BaseAgent


class ExecutorAgent(BaseAgent):
    """
    Agent responsible for executing tasks using the Ollama API.
    
    Takes a user task and sends it to the local LLM to generate a response.
    """
    
    def __init__(self, ollama_api_url: str = "http://localhost:11434/api/generate", 
                 model: str = "llama2", temperature: float = 0.7):
        """
        Initialize executor agent.
        
        Args:
            ollama_api_url: URL for Ollama API
            model: LLM model to use
            temperature: Temperature for LLM responses
        """
        super().__init__(name="ExecutorAgent", model=model, temperature=temperature)
        self.ollama_api_url = ollama_api_url
        self.logger.info(f"Executor Agent connected to: {ollama_api_url}")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using the Ollama API.
        
        Args:
            input_data: Dictionary with 'task' and optional 'prompt' keys
            
        Returns:
            Dictionary with 'task', 'response', and 'success' keys
        """
        try:
            task = input_data.get("task", "")
            prompt = input_data.get("prompt", None)
            
            if not task:
                raise ValueError("Task is required in input_data")
            
            # Construct the prompt
            if prompt:
                full_prompt = f"{prompt}\n\nTask: {task}"
            else:
                full_prompt = task
            
            self.logger.debug(f"Executing task: {task[:100]}...")
            
            # Call Ollama API
            response = self._call_ollama(full_prompt)
            
            self.logger.info(f"Task executed successfully")
            
            return {
                "task": task,
                "response": response,
                "success": True,
                "model": self.model
            }
        
        except Exception as e:
            self.logger.error(f"Error executing task: {str(e)}")
            return {
                "task": input_data.get("task", ""),
                "response": str(e),
                "success": False,
                "model": self.model
            }
    
    def _call_ollama(self, prompt: str) -> str:
        """
        Call the Ollama API.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            The model's response
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": self.temperature
            }
            
            response = requests.post(self.ollama_api_url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
        
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama API at {self.ollama_api_url}. "
                "Make sure Ollama is running locally."
            )
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama API request timed out")
        except json.JSONDecodeError:
            raise ValueError("Invalid response from Ollama API")
        except Exception as e:
            raise Exception(f"Error calling Ollama API: {str(e)}")
