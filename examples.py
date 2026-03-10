# Example usage scripts for the Self-Improving AI Agent Framework
#
# Author: Selvagurunathan Ramalingam
# Date: March 10, 2026
# Version: 1.0
#
# Description:
#     Five practical examples demonstrating different features
#     of the Self-Improving AI Agent Framework

from main import SelfImprovingAIAgent


def example_1_basic_execution():
    """Example 1: Basic task execution."""
    print("\n" + "="*60)
    print("Example 1: Basic Task Execution")
    print("="*60)
    
    agent = SelfImprovingAIAgent(max_iterations=2)
    
    task = "Write a Python function that calculates the factorial of a number"
    
    result = agent.execute_task(task, verbose=True)
    
    print(f"\nFinal Score: {result['final_score']}/10")
    print(f"Iterations Performed: {len(result['iterations'])}")


def example_2_use_memory():
    """Example 2: Using memory for similar tasks."""
    print("\n" + "="*60)
    print("Example 2: Using Memory for Similar Tasks")
    print("="*60)
    
    agent = SelfImprovingAIAgent(max_iterations=2)
    
    # First task
    task1 = "Write a Python function to calculate factorial"
    print(f"\nTask 1: {task1}")
    result1 = agent.execute_task(task1, use_memory=True, verbose=False)
    print(f"Score: {result1['final_score']}/10")
    
    # Similar task - should benefit from memory
    task2 = "Write a Python function to calculate fibonacci sequence"
    print(f"\nTask 2: {task2}")
    result2 = agent.execute_task(task2, use_memory=True, verbose=False)
    print(f"Score: {result2['final_score']}/10")


def example_3_statistics():
    """Example 3: View statistics and memory."""
    print("\n" + "="*60)
    print("Example 3: Statistics and Memory")
    print("="*60)
    
    agent = SelfImprovingAIAgent()
    
    stats = agent.get_statistics()
    
    print(f"\nTotal Memories: {stats['total_memories']}")
    print(f"Task Executions: {stats['task_executions']}")
    print(f"Evaluations: {stats['evaluations']}")
    print(f"Prompt Versions: {stats['prompt_versions']}")
    print(f"Average Score: {stats['avg_score']:.2f}")
    print(f"Unique Tasks: {len(stats['tasks'])}")


def example_4_task_history():
    """Example 4: View task history."""
    print("\n" + "="*60)
    print("Example 4: Task History")
    print("="*60)
    
    agent = SelfImprovingAIAgent()
    
    task = "Write a Python function to sort a list"
    
    # Execute the task
    print(f"\nExecuting: {task}")
    result = agent.execute_task(task, verbose=False)
    
    # Get history
    print(f"\nTask History:")
    history = agent.get_task_history(task)
    for entry in history:
        print(f"  - {entry.get('memory_type', 'unknown')}: {entry.get('timestamp', 'N/A')}")


def example_5_batch_processing():
    """Example 5: Batch processing multiple tasks."""
    print("\n" + "="*60)
    print("Example 5: Batch Processing")
    print("="*60)
    
    agent = SelfImprovingAIAgent(max_iterations=1)
    
    tasks = [
        "Write a function to check if a number is prime",
        "Write a function to reverse a string",
        "Write a function to find the maximum element in a list",
    ]
    
    results = []
    for i, task in enumerate(tasks, 1):
        print(f"\nProcessing task {i}/{len(tasks)}: {task[:50]}...")
        result = agent.execute_task(task, verbose=False)
        results.append({
            "task": task,
            "score": result['final_score'],
            "iterations": len(result['iterations'])
        })
    
    print("\n" + "-"*60)
    print("Batch Results Summary:")
    print("-"*60)
    for r in results:
        print(f"Score: {r['score']}/10 - {r['task'][:40]}...")
    
    avg_score = sum(r['score'] for r in results) / len(results)
    print(f"\nAverage Score: {avg_score:.1f}/10")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        
        examples = {
            "1": example_1_basic_execution,
            "2": example_2_use_memory,
            "3": example_3_statistics,
            "4": example_4_task_history,
            "5": example_5_batch_processing,
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Unknown example: {example_num}")
            print("Available examples: 1, 2, 3, 4, 5")
    else:
        print("\n" + "="*60)
        print("Self-Improving AI Agent - Examples")
        print("="*60)
        print("\nUsage: python examples.py <example_number>")
        print("\nAvailable Examples:")
        print("  1 - Basic Task Execution")
        print("  2 - Using Memory for Similar Tasks")
        print("  3 - Statistics and Memory View")
        print("  4 - Task History")
        print("  5 - Batch Processing")
        print("\nExample: python examples.py 1")
