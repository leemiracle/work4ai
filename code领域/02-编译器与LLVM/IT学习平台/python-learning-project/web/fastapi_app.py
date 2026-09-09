from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn


app = FastAPI(title="学习项目API", version="1.0.0")


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False


tasks_db: List[Task] = [
    Task(id=1, title="学习Python", description="掌握Python基础语法", completed=False),
    Task(id=2, title="实践算法", description="实现常见数据结构", completed=True),
    Task(id=3, title="Web开发", description="构建RESTful API", completed=False),
]


@app.get("/")
def read_root():
    return {"message": "欢迎使用FastAPI学习项目", "version": "1.0.0"}


@app.get("/tasks", response_model=List[Task])
def get_tasks(completed: Optional[bool] = None):
    if completed is not None:
        return [task for task in tasks_db if task.completed == completed]
    return tasks_db


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = next((task for task in tasks_db if task.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    return task


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: Task):
    if any(t.id == task.id for t in tasks_db):
        raise HTTPException(status_code=400, detail="任务ID已存在")
    tasks_db.append(task)
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: Task):
    task = next((task for task in tasks_db if task.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    
    task.title = task_update.title
    task.description = task_update.description
    task.completed = task_update.completed
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks_db
    task = next((task for task in tasks_db if task.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    
    tasks_db = [t for t in tasks_db if t.id != task_id]
    return {"message": "任务已删除"}


@app.get("/stats")
def get_stats():
    total = len(tasks_db)
    completed = sum(1 for task in tasks_db if task.completed)
    pending = total - completed
    
    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "completion_rate": completed / total if total > 0 else 0
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)