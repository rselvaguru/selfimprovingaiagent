"""
Evaluator Agent - Quality Evaluation Component

Author: Selvagurunathan Ramalingam
Date: March 10, 2026
Version: 1.0

Description:
    Agent responsible for evaluating the quality of AI responses.
    Scores responses, identifies mistakes, and provides improvement suggestions.
"""

import requests
import json
from typing import Any, Dict
from agents.base_agent import BaseAgent


class EvaluatorAgent(BaseAgent):
    """
    Agent responsible for evaluating the quality of AI responses.
    
    Scores responses, identifies mistakes, and provides improvement suggestions.
    """
    
    def __init__(self, ollama_api_url: str = "http://localhost:11434/api/generate",
                 model: str = "llama2", temperature: float = 0.3):
        """
        Initialize evaluator agent.
        
        Args:
            ollama_api_url: URL for Ollama API
            model: LLM model to use
            temperature: Lower temperature for more consistent evaluation
        """
        super().__init__(name="EvaluatorAgent", model=model, temperature=temperature)
        self.ollama_api_url = ollama_api_url
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an AI response.
        
        Args:
            input_data: Dictionary with 'task', 'response' keys
            
        Returns:
            Dictionary with 'score', 'feedback', 'strengths', 'weaknesses', 'suggestions'
        """
        try:
            task = input_data.get("task", "")
            response = input_data.get("response", "")
            
            if not task or not response:
                raise ValueError("Both 'task' and 'response' are required")
            
            self.logger.debug(f"Evaluating response for task: {task[:100]}...")
            
            # Generate evaluation prompt
            evaluation_prompt = self._create_evaluation_prompt(task, response)
            
            # Get evaluation from LLM
            evaluation = self._call_ollama(evaluation_prompt)
            
            # Parse evaluation results
            parsed_eval = self._parse_evaluation(evaluation)
            
            self.logger.info(f"Evaluation complete. Score: {parsed_eval['score']}/10")
            
            return {
                "task": task,
                "response": response,
                "score": parsed_eval.get("score", 0),
                "feedback": parsed_eval.get("feedback", ""),
                "strengths": parsed_eval.get("strengths", []),
                "weaknesses": parsed_eval.get("weaknesses", []),
                "suggestions": parsed_eval.get("suggestions", []),
                "raw_evaluation": evaluation
            }
        
        except Exception as e:
            self.logger.error(f"Error evaluating response: {str(e)}")
            return {
                "task": input_data.get("task", ""),
                "response": input_data.get("response", ""),
                "score": 0,
                "feedback": str(e),
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "error": True
            }
    
    def _create_evaluation_prompt(self, task: str, response: str) -> str:
        """
        Create a prompt for evaluating the response.
        
        Args:
            task: The original task
            response: The AI-generated response
            
        Returns:
            Evaluation prompt
        """
        return f"""Evaluate the following response to a task.

TASK: {task}

RESPONSE: {response}

Please provide:
1. A score from 1-10
2. Overall feedback
3. Key strengths (bullet points)
4. Key weaknesses (bullet points)
5. Specific suggestions for improvement

Format your response clearly with these sections labeled."""
    
    def _parse_evaluation(self, evaluation: str) -> Dict[str, Any]:
        """
        Parse the evaluation response from the LLM.
        
        Args:
            evaluation: Raw evaluation text from LLM
            
        Returns:
            Parsed evaluation dictionary
        """
        try:
            parsed = {
                "score": 5,
                "feedback": evaluation,
                "strengths": [],
                "weaknesses": [],
                "suggestions": []
            }
            
            # Extract score
            lines = evaluation.split('\n')
            for line in lines:
                if 'score' in line.lower():
                    # Try to extract a number
                    for word in line.split():
                        try:
                            num = int(word)
                            if 1 <= num <= 10:
                                parsed["score"] = num
                                break
                        except ValueError:
                            continue
                    break
            
            # Extract sections
            sections = {
                "strengths": [],
                "weaknesses": [],
                "suggestions": []
            }
            
            current_section = None
            for line in lines:
                line_lower = line.lower()
                
                if "strength" in line_lower:
                    current_section = "strengths"
                elif "weakness" in line_lower:
                    current_section = "weaknesses"
                elif "suggestion" in line_lower or "improvement" in line_lower:
                    current_section = "suggestions"
                elif current_section and line.strip().startswith(("-", "*", "•")):
                    item = line.strip()[1:].strip()
                    if item:
                        sections[current_section].append(item)
            
            parsed.update(sections)
            
            return parsed
        
        except Exception as e:
            self.logger.warning(f"Could not parse evaluation: {str(e)}")
            return {
                "score": 5,
                "feedback": evaluation,
                "strengths": [],
                "weaknesses": [],
                "suggestions": []
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
