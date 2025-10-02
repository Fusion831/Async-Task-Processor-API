import time
import random
from celery import Celery
from .celery_app import celery_app
from .db import save_result, mark_task_failed
from typing import Optional

@celery_app.task(bind=True)
def heavy_computation_task(self, task_id: str, data: Optional[dict] = None):
    """
    Simulates a heavy computation task that takes time to process.
    In a real application, this could be ML inference, data processing, etc.
    """
    try:
        # Simulate heavy computation (5-10 seconds)
        computation_time = random.uniform(5, 10)
        
        for i in range(int(computation_time)):
            time.sleep(1)
            # Update task progress (optional)
            self.update_state(state='PROGRESS', meta={'progress': (i + 1) / computation_time * 100})
        
        # Simulate some computation result
        # In real scenario, this would be the actual result of processing
        result = sum(range(1000000))  # Simple computation
        if data:
            # Incorporate input data into result somehow
            result += hash(str(data)) % 1000
        
        # Save result to database
        save_result(task_id, result)
        
        return {
            'task_id': task_id,
            'result': result,
            'status': 'completed',
            'message': 'Task completed successfully'
        }
        
    except Exception as exc:
        # Mark task as failed in database
        error_message = str(exc)
        mark_task_failed(task_id, error_message)
        
        # Re-raise the exception so Celery can handle it
        raise self.retry(exc=exc, countdown=60, max_retries=3)