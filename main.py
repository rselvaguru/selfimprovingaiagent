"""
Self-Improving AI Agent Framework - Main Orchestrator

Author: Selvagurunathan Ramalingam
Date: March 10, 2026
Version: 1.0

Description:
    Main orchestrator for the self-improving AI agent framework.
    Coordinates the execution, evaluation, optimization, and memory storage
    in a continuous learning loop.
"""

import sys
from typing import Dict, Any, Optional
from pathlib import Path

from agents import ExecutorAgent, EvaluatorAgent, OptimizerAgent
from memory import MemoryManager
from utils.logger import Logger


class SelfImprovingAIAgent:
    """
    Main orchestrator for the self-improving AI agent framework.
    
    Coordinates the execution, evaluation, optimization, and memory storage
    in a continuous learning loop.
    """
    
    def __init__(self, ollama_api_url: str = "http://localhost:11434/api/generate",
                 model: str = "llama2", max_iterations: int = 3,
                 persist_dir: str = "./chroma_data"):
        """
        Initialize the self-improving AI agent.
        
        Args:
            ollama_api_url: URL for Ollama API
            model: LLM model to use
            max_iterations: Maximum iterations for improvement loop
            persist_dir: Directory for persistent memory storage
        """
        self.logger = Logger("SelfImprovingAIAgent")
        self.ollama_api_url = ollama_api_url
        self.model = model
        self.max_iterations = max_iterations
        
        # Initialize agents
        self.executor = ExecutorAgent(ollama_api_url=ollama_api_url, model=model)
        self.evaluator = EvaluatorAgent(ollama_api_url=ollama_api_url, model=model)
        self.optimizer = OptimizerAgent(ollama_api_url=ollama_api_url, model=model)
        
        # Initialize memory
        self.memory = MemoryManager(persist_dir=persist_dir)
        
        # Load base prompt
        self.base_prompt = self._load_base_prompt()
        
        self.logger.info("Self-Improving AI Agent initialized")
    
    def execute_task(self, task: str, use_memory: bool = True, 
                    verbose: bool = True) -> Dict[str, Any]:
        """
        Execute a task through the learning loop.
        
        Args:
            task: The task to complete
            use_memory: Whether to use memory for retrieving similar tasks
            verbose: Whether to print detailed logs
            
        Returns:
            Dictionary with final response, evaluations, and improvements
        """
        self.logger.info(f"Starting task execution: {task[:100]}...")
        
        # Initialize tracking variables
        current_prompt = None
        best_response = None
        best_score = 0
        iteration_results = []
        
        # Retrieve best prompt from memory if available
        if use_memory:
            best_prompt_record = self.memory.retrieve_best_prompt(task)
            if best_prompt_record:
                current_prompt = best_prompt_record["prompt"]
                best_score = best_prompt_record["score"]
                if verbose:
                    print(f"\n[Memory] Found previous best prompt with score: {best_score}")
        
        # Use base prompt if no previous version exists
        if not current_prompt:
            current_prompt = self._create_task_prompt(task)
        
        # Main improvement loop
        for iteration in range(self.max_iterations):
            if verbose:
                print(f"\n{'='*60}")
                print(f"Iteration {iteration + 1}/{self.max_iterations}")
                print(f"{'='*60}")
            
            self.logger.info(f"Iteration {iteration + 1}: Executing task")
            
            # 1. Execute task
            execution_result = self._execute_step(task, current_prompt, verbose)
            
            if not execution_result["success"]:
                self.logger.error(f"Task execution failed: {execution_result['error']}")
                return {
                    "task": task,
                    "success": False,
                    "error": execution_result["error"],
                    "iterations": 0
                }
            
            current_response = execution_result["response"]
            best_response = current_response
            
            # 2. Evaluate response
            evaluation_result = self._evaluate_step(task, current_response, verbose)
            current_score = evaluation_result["score"]
            
            iteration_data = {
                "iteration": iteration + 1,
                "score": current_score,
                "feedback": evaluation_result["feedback"],
                "response": current_response
            }
            iteration_results.append(iteration_data)
            
            # Store evaluation in memory
            self.memory.store_evaluation(
                task=task,
                score=current_score,
                feedback=evaluation_result["feedback"],
                suggestions=evaluation_result["suggestions"],
                metadata={"iteration": iteration + 1}
            )
            
            # 3. Check if we should continue
            if current_score >= 8 or iteration == self.max_iterations - 1:
                if verbose:
                    print(f"\n[Result] Stopping at iteration {iteration + 1}")
                    if current_score >= 8:
                        print(f"[Result] Score {current_score}/10 - Target reached!")
                break
            
            # 4. Optimize prompt
            optimization_result = self._optimize_step(
                task=task,
                current_prompt=current_prompt,
                feedback=evaluation_result["feedback"],
                suggestions=evaluation_result["suggestions"],
                score=current_score,
                verbose=verbose
            )
            
            if optimization_result["success"]:
                current_prompt = optimization_result["improved_prompt"]
                
                # Store prompt version in memory
                self.memory.store_prompt_version(
                    task=task,
                    prompt=current_prompt,
                    iteration=iteration + 1,
                    score=current_score
                )
                
                if verbose:
                    print(f"\n[Optimization] Prompt updated")
                    if optimization_result.get("changes_made"):
                        for change in optimization_result["changes_made"][:3]:
                            print(f"  - {change}")
        
        # Store final task execution
        self.memory.store_task_execution(
            task=task,
            response=best_response,
            metadata={"final_score": current_score, "iterations": len(iteration_results)}
        )
        
        self.logger.info(f"Task completed. Final score: {current_score}/10")
        
        return {
            "task": task,
            "success": True,
            "final_response": best_response,
            "final_score": current_score,
            "iterations": iteration_results,
            "best_prompt_version": current_prompt,
            "improvements_made": len(iteration_results) - 1
        }
    
    def _execute_step(self, task: str, prompt: str, verbose: bool = True) -> Dict[str, Any]:
        """Execute the task using the executor agent."""
        try:
            result = self.executor.execute({
                "task": task,
                "prompt": prompt
            })
            
            if verbose and result["success"]:
                print(f"\n[Execution] Task completed")
                print(f"Response preview: {result['response'][:200]}...")
            
            return {
                "success": result["success"],
                "response": result["response"],
                "error": None if result["success"] else result["response"]
            }
        
        except Exception as e:
            self.logger.error(f"Execution error: {str(e)}")
            return {
                "success": False,
                "response": None,
                "error": str(e)
            }
    
    def _evaluate_step(self, task: str, response: str, verbose: bool = True) -> Dict[str, Any]:
        """Evaluate the response using the evaluator agent."""
        try:
            result = self.evaluator.execute({
                "task": task,
                "response": response
            })
            
            if verbose:
                print(f"\n[Evaluation] Score: {result['score']}/10")
                print(f"Feedback: {result['feedback'][:200]}...")
            
            return {
                "score": result.get("score", 0),
                "feedback": result.get("feedback", ""),
                "strengths": result.get("strengths", []),
                "weaknesses": result.get("weaknesses", []),
                "suggestions": result.get("suggestions", [])
            }
        
        except Exception as e:
            self.logger.error(f"Evaluation error: {str(e)}")
            return {
                "score": 0,
                "feedback": str(e),
                "strengths": [],
                "weaknesses": [],
                "suggestions": []
            }
    
    def _optimize_step(self, task: str, current_prompt: str, feedback: str,
                      suggestions: list, score: int, verbose: bool = True) -> Dict[str, Any]:
        """Optimize the prompt using the optimizer agent."""
        try:
            result = self.optimizer.execute({
                "task": task,
                "current_prompt": current_prompt,
                "feedback": feedback,
                "suggestions": suggestions,
                "score": score
            })
            
            return {
                "success": not result.get("error", False),
                "improved_prompt": result.get("improved_prompt", current_prompt),
                "changes_made": result.get("changes_made", []),
                "rationale": result.get("rationale", "")
            }
        
        except Exception as e:
            self.logger.error(f"Optimization error: {str(e)}")
            return {
                "success": False,
                "improved_prompt": current_prompt,
                "changes_made": [],
                "error": str(e)
            }
    
    def _load_base_prompt(self) -> str:
        """Load the base prompt from file."""
        try:
            prompt_file = Path(__file__).parent / "prompts" / "base_prompt.txt"
            if prompt_file.exists():
                return prompt_file.read_text().strip()
        except Exception as e:
            self.logger.warning(f"Could not load base prompt file: {str(e)}")
        
        return "You are an expert assistant. Complete the following task with high quality and accuracy."
    
    def _create_task_prompt(self, task: str) -> str:
        """Create a task-specific prompt."""
        return f"{self.base_prompt}\n\n{task}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the agent's memory and performance."""
        return self.memory.get_statistics()
    
    def get_task_history(self, task: str) -> list:
        """Get the execution history for a specific task."""
        return self.memory.get_task_history(task)


def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Self-Improving AI Agent Framework"
    )
    parser.add_argument(
        "task",
        nargs="?",
        help="The task to execute"
    )
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434/api/generate",
        help="Ollama API URL"
    )
    parser.add_argument(
        "--model",
        default="llama2",
        help="LLM model to use"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Maximum iterations for improvement loop"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode"
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = SelfImprovingAIAgent(
        ollama_api_url=args.ollama_url,
        model=args.model,
        max_iterations=args.iterations
    )
    
    # Show statistics
    if args.stats:
        stats = agent.get_statistics()
        print("\n=== Memory Statistics ===")
        print(f"Total memories: {stats.get('total_memories', 0)}")
        print(f"Task executions: {stats.get('task_executions', 0)}")
        print(f"Evaluations: {stats.get('evaluations', 0)}")
        print(f"Prompt versions: {stats.get('prompt_versions', 0)}")
        print(f"Average score: {stats.get('avg_score', 0):.2f}")
        print(f"Unique tasks: {len(stats.get('tasks', []))}")
        return
    
    # Interactive mode
    if args.interactive:
        print("\n=== Self-Improving AI Agent - Interactive Mode ===")
        print("Enter 'quit' to exit\n")
        
        while True:
            try:
                task = input("Enter task: ").strip()
                
                if task.lower() == "quit":
                    print("Goodbye!")
                    break
                
                if not task:
                    continue
                
                print("\nProcessing...")
                result = agent.execute_task(task, verbose=True)
                
                print(f"\n{'='*60}")
                print(f"FINAL RESULT")
                print(f"{'='*60}")
                print(f"Score: {result['final_score']}/10")
                print(f"Iterations: {len(result['iterations'])}")
                print(f"\nResponse:\n{result['final_response']}")
                print(f"\n{'='*60}\n")
            
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
        
        return
    
    # Single task execution
    if args.task:
        print("\n=== Self-Improving AI Agent ===\n")
        result = agent.execute_task(args.task, verbose=True)
        
        print(f"\n{'='*60}")
        print(f"FINAL RESULT")
        print(f"{'='*60}")
        
        if result.get('success'):
            print(f"Score: {result.get('final_score', 'N/A')}/10")
            print(f"Iterations: {len(result.get('iterations', []))}")
            print(f"\nResponse:\n{result.get('final_response', 'No response')}")
        else:
            print(f"Task execution failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n{'='*60}")
    
    else:
        print("Usage: python main.py <task> [options]")
        print("       python main.py --interactive  (for interactive mode)")
        print("       python main.py --stats        (to show statistics)")
        print("\nRun 'python main.py --help' for more options")


if __name__ == "__main__":
    main()
