"""
FastAPI REST Server - API Interface

Author: Selvagurunathan Ramalingam
Date: March 10, 2026
Version: 1.0

Description:
    REST API server for the Self-Improving AI Agent Framework using FastAPI.
    Provides endpoints for task execution, statistics, history, and batch processing.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from main import SelfImprovingAIAgent


# Pydantic models
class TaskRequest(BaseModel):
    """Request model for task execution."""
    task: str = Field(..., description="The task to execute")
    use_memory: bool = Field(default=True, description="Use memory for context")
    max_iterations: int = Field(default=3, ge=1, le=10, description="Max iterations")


class IterationResult(BaseModel):
    """Result from a single iteration."""
    iteration: int
    score: int
    feedback: str
    response: str


class TaskResponse(BaseModel):
    """Response model for task execution."""
    success: bool
    task: str
    final_score: int
    final_response: str
    iterations: List[IterationResult]
    improvements_made: int


class StatisticsResponse(BaseModel):
    """Response model for statistics."""
    total_memories: int
    task_executions: int
    evaluations: int
    prompt_versions: int
    avg_score: float
    unique_tasks: int


class TaskHistoryResponse(BaseModel):
    """Response model for task history."""
    task: str
    history: List[Dict[str, Any]]


# Initialize FastAPI app
app = FastAPI(
    title="Self-Improving AI Agent API",
    description="API for the Self-Improving AI Agent Framework",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = SelfImprovingAIAgent()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Self-Improving AI Agent API",
        "version": "1.0.0",
        "description": "An autonomous AI agent framework that improves its own performance",
        "endpoints": {
            "execute_task": "/execute",
            "statistics": "/statistics",
            "task_history": "/history/{task_id}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Self-Improving AI Agent"}


@app.post("/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """
    Execute a task through the learning loop.
    
    The task will be executed, evaluated, and the prompt will be optimized
    based on feedback for up to `max_iterations` iterations.
    """
    try:
        result = agent.execute_task(
            task=request.task,
            use_memory=request.use_memory,
            verbose=False
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Task execution failed")
            )
        
        return TaskResponse(
            success=True,
            task=request.task,
            final_score=result["final_score"],
            final_response=result["final_response"],
            iterations=[
                IterationResult(**iter_result)
                for iter_result in result["iterations"]
            ],
            improvements_made=result["improvements_made"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing task: {str(e)}"
        )


@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """
    Get statistics about the agent's memory and performance.
    
    Returns information about stored memories, average scores, and unique tasks.
    """
    try:
        stats = agent.get_statistics()
        
        return StatisticsResponse(
            total_memories=stats.get("total_memories", 0),
            task_executions=stats.get("task_executions", 0),
            evaluations=stats.get("evaluations", 0),
            prompt_versions=stats.get("prompt_versions", 0),
            avg_score=stats.get("avg_score", 0),
            unique_tasks=len(stats.get("tasks", []))
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@app.get("/history/{task_id}", response_model=TaskHistoryResponse)
async def get_task_history(task_id: str):
    """
    Get the execution history for a specific task.
    
    Returns all previous executions, evaluations, and prompt improvements.
    """
    try:
        history = agent.get_task_history(task_id)
        
        return TaskHistoryResponse(
            task=task_id,
            history=history
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )


@app.post("/batch-execute")
async def batch_execute(tasks: List[TaskRequest]):
    """
    Execute multiple tasks in batch.
    
    Returns results for each task.
    """
    try:
        results = []
        
        for request in tasks:
            result = agent.execute_task(
                task=request.task,
                use_memory=request.use_memory,
                verbose=False
            )
            
            results.append({
                "task": request.task,
                "success": result["success"],
                "score": result.get("final_score", 0),
                "iterations": len(result.get("iterations", []))
            })
        
        return {"results": results, "total": len(results), "successful": sum(1 for r in results if r["success"])}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing batch: {str(e)}"
        )


def main():
    """Run the FastAPI server."""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
