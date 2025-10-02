from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from typing import Optional
from .db import create_task, get_task
from .tasks import heavy_computation_task

app = FastAPI(title="Async Task Processor API", version="1.0.0")

class TaskData(BaseModel):
    data: Optional[dict] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[int] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

@app.get('/health')
def health_check():
    return {"status": "ok"}

@app.post("/process", response_model=TaskResponse)
def process_task(task_data: TaskData = TaskData()):
    """
    Non-blocking endpoint that creates a background task for heavy computation.
    Returns immediately with a task_id for status checking.
    """
    task_id = str(uuid.uuid4())
    
    # Create task record in database
    create_task(task_id)
    
    
    heavy_computation_task.delay(task_id, task_data.data)
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Task queued for processing"
    )

@app.get("/results/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    """
    Get the status and result of a task by task_id.
    """
    task = get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatusResponse(
        task_id=task['task_id'],
        status=task['status'],
        result=task['result'],
        error_message=task['error_message'],
        created_at=task['created_at'].isoformat() if task['created_at'] else None,
        completed_at=task['completed_at'].isoformat() if task['completed_at'] else None
    )
