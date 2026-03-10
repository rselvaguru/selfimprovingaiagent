"""
Optimizer Agent - Prompt Optimization Component

Author: Selvagurunathan Ramalingam
Date: March 10, 2026
Version: 1.0

Description:
    Agent responsible for optimizing prompts based on evaluator feedback.
    Uses feedback to improve prompts for better future responses.
"""

import requests
import json
from typing import Any, Dict, List
from agents.base_agent import BaseAgent


class OptimizerAgent(BaseAgent):
    """
    Agent responsible for optimizing prompts based on evaluator feedback.
    
    Uses feedback to improve prompts for better future responses.
    """
    
    def __init__(self, ollama_api_url: str = "http://localhost:11434/api/generate",
                 model: str = "llama2", temperature: float = 0.5):
        """
        Initialize optimizer agent.
        
        Args:
            ollama_api_url: URL for Ollama API
            model: LLM model to use
            temperature: Temperature for optimization
        """
        super().__init__(name="OptimizerAgent", model=model, temperature=temperature)
        self.ollama_api_url = ollama_api_url
        self.prompt_history: List[Dict[str, Any]] = []
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize a prompt based on evaluation feedback.
        
        Args:
            input_data: Dictionary with 'task', 'current_prompt', 'feedback', 'suggestions'
            
        Returns:
            Dictionary with 'improved_prompt', 'changes_made', 'rationale'
        """
        try:
            task = input_data.get("task", "")
            current_prompt = input_data.get("current_prompt", "")
            feedback = input_data.get("feedback", "")
            suggestions = input_data.get("suggestions", [])
            score = input_data.get("score", 5)
            
            if not task:
                raise ValueError("Task is required")
            
            # If no prompt exists, create a new one
            if not current_prompt:
                current_prompt = self._create_base_prompt(task)
            
            self.logger.debug(f"Optimizing prompt for task: {task[:100]}...")
            
            # Generate optimization prompt
            optimization_prompt = self._create_optimization_prompt(
                task, current_prompt, feedback, suggestions, score
            )
            
            # Get improved prompt from LLM
            improved_prompt = self._call_ollama(optimization_prompt)
            
            # Store in history
            improvement_record = {
                "iteration": len(self.prompt_history),
                "task": task,
                "old_prompt": current_prompt,
                "new_prompt": improved_prompt,
                "score": score,
                "feedback": feedback
            }
            self.prompt_history.append(improvement_record)
            
            self.logger.info(f"Prompt optimized. Iteration: {len(self.prompt_history)}")
            
            return {
                "task": task,
                "improved_prompt": improved_prompt,
                "previous_prompt": current_prompt,
                "score": score,
                "changes_made": self._identify_changes(current_prompt, improved_prompt),
                "rationale": f"Improvements based on score {score}/10 and feedback: {feedback}",
                "iteration": len(self.prompt_history)
            }
        
        except Exception as e:
            self.logger.error(f"Error optimizing prompt: {str(e)}")
            return {
                "task": input_data.get("task", ""),
                "improved_prompt": input_data.get("current_prompt", ""),
                "error": True,
                "error_message": str(e)
            }
    
    def _create_base_prompt(self, task: str) -> str:
        """
        Create a base prompt for a task if none exists.
        
        Args:
            task: The task description
            
        Returns:
            A base prompt
        """
        return f"""You are an expert assistant. 
Complete the following task with high quality and accuracy:

{task}

Provide a comprehensive and well-structured response."""
    
    def _create_optimization_prompt(self, task: str, current_prompt: str, 
                                   feedback: str, suggestions: List[str], 
                                   score: int) -> str:
        """
        Create a prompt for optimizing the existing prompt.
        
        Args:
            task: The original task
            current_prompt: The current prompt template
            feedback: Feedback from the evaluator
            suggestions: List of improvement suggestions
            score: Score from evaluation
            
        Returns:
            Optimization prompt
        """
        suggestions_text = "\n".join(f"- {s}" for s in suggestions) if suggestions else "No specific suggestions"
        
        return f"""You are a prompt optimization expert. 

The current prompt for a task scored {score}/10 and received this feedback:
FEEDBACK: {feedback}

IMPROVEMENT SUGGESTIONS:
{suggestions_text}

CURRENT PROMPT:
{current_prompt}

TASK DESCRIPTION:
{task}

Please create an improved version of the prompt that:
1. Addresses the weaknesses identified in the feedback
2. Incorporates the improvement suggestions
3. Maintains clarity and specificity
4. Adds any additional instructions that could help achieve better results

Provide ONLY the improved prompt, without explanations."""
    
    def _identify_changes(self, old_prompt: str, new_prompt: str) -> List[str]:
        """
        Identify key changes between old and new prompts.
        
        Args:
            old_prompt: Previous prompt
            new_prompt: New optimized prompt
            
        Returns:
            List of identified changes
        """
        changes = []
        
        # Simple heuristics for identifying changes
        old_words = set(old_prompt.lower().split())
        new_words = set(new_prompt.lower().split())
        
        added = new_words - old_words
        removed = old_words - new_words
        
        if len(new_prompt) > len(old_prompt):
            changes.append(f"Expanded prompt by {len(new_prompt) - len(old_prompt)} characters")
        elif len(new_prompt) < len(old_prompt):
            changes.append(f"Condensed prompt by {len(old_prompt) - len(new_prompt)} characters")
        
        if added:
            key_added = [w for w in added if len(w) > 5][:3]
            if key_added:
                changes.append(f"Added focus on: {', '.join(key_added)}")
        
        if removed:
            key_removed = [w for w in removed if len(w) > 5][:3]
            if key_removed:
                changes.append(f"Removed emphasis on: {', '.join(key_removed)}")
        
        return changes if changes else ["Prompt structure refined"]
    
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
    
    def get_prompt_history(self) -> List[Dict[str, Any]]:
        """Get the history of prompt improvements."""
        return self.prompt_history
