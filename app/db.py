import os
from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData, DateTime, Text
from sqlalchemy.sql import insert, select, update
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")


engine = create_engine(DATABASE_URL)
metadata = MetaData()

tasks_table = Table(
    "tasks", metadata,
    Column("task_id", String, primary_key=True),
    Column("status", String, default="pending"),  # pending, completed, failed
    Column("result", Integer, nullable=True),
    Column("error_message", Text, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("completed_at", DateTime, nullable=True),
)

metadata.create_all(engine)

def create_task(task_id: str):
    """Create a new task with pending status"""
    with engine.begin() as conn:
        conn.execute(insert(tasks_table).values(
            task_id=task_id,
            status="pending",
            created_at=datetime.utcnow()
        ))

def save_result(task_id: str, result: int):
    """Save the result and mark task as completed"""
    with engine.begin() as conn:
        conn.execute(update(tasks_table)
                    .where(tasks_table.c.task_id == task_id)
                    .values(
                        result=result,
                        status="completed",
                        completed_at=datetime.utcnow()
                    ))

def mark_task_failed(task_id: str, error_message: str):
    """Mark a task as failed with error message"""
    with engine.begin() as conn:
        conn.execute(update(tasks_table)
                    .where(tasks_table.c.task_id == task_id)
                    .values(
                        status="failed",
                        error_message=error_message,
                        completed_at=datetime.utcnow()
                    ))

def get_task(task_id: str):
    """Get task details by task_id"""
    with engine.begin() as conn:
        res = conn.execute(select(tasks_table).where(tasks_table.c.task_id == task_id)).fetchone()
        return dict(res) if res else None
