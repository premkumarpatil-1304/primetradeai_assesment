from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from app.db.mongodb import mongodb
from app.api.v1.deps import verify_access_token
from app.models.task import TaskCreate, TaskOut

router = APIRouter()

# Helper: convert MongoDB document to Python dict
def serialize_task(task):
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task["description"],
        "owner": task["owner"]
    }

# 🟢 Create a new task (any logged-in user)
@router.post("/", response_model=TaskOut)
async def create_task(task: TaskCreate, token_data: dict = Depends(verify_access_token)):
    if mongodb.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    user_email = token_data["sub"]
    tasks_col = mongodb.db["tasks"]

    new_task = {
        "title": task.title,
        "description": task.description,
        "owner": user_email
    }

    result = await tasks_col.insert_one(new_task)
    saved_task = await tasks_col.find_one({"_id": result.inserted_id})
    return serialize_task(saved_task)

# 🔵 Get all tasks (admin only)
@router.get("/", response_model=List[TaskOut])
async def get_all_tasks(token_data: dict = Depends(verify_access_token)):
    if mongodb.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    if token_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    tasks_col = mongodb.db["tasks"]
    tasks = await tasks_col.find().to_list(100)
    return [serialize_task(t) for t in tasks]

# 🟣 Get my tasks
@router.get("/me", response_model=List[TaskOut])
async def get_my_tasks(token_data: dict = Depends(verify_access_token)):
    if mongodb.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    user_email = token_data["sub"]
    tasks_col = mongodb.db["tasks"]
    tasks = await tasks_col.find({"owner": user_email}).to_list(100)
    return [serialize_task(t) for t in tasks]

# 🟠 Update my task
@router.put("/{task_id}", response_model=TaskOut)
async def update_task(task_id: str, task: TaskCreate, token_data: dict = Depends(verify_access_token)):
    if mongodb.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    user_email = token_data["sub"]
    tasks_col = mongodb.db["tasks"]

    result = await tasks_col.update_one(
        {"_id": ObjectId(task_id), "owner": user_email},
        {"$set": {"title": task.title, "description": task.description}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found or not owned by you")

    updated_task = await tasks_col.find_one({"_id": ObjectId(task_id)})
    return serialize_task(updated_task)

# 🔴 Delete my task (user or admin)
@router.delete("/{task_id}")
async def delete_task(task_id: str, token_data: dict = Depends(verify_access_token)):
    if mongodb.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    user_email = token_data["sub"]
    user_role = token_data["role"]
    tasks_col = mongodb.db["tasks"]

    query = {"_id": ObjectId(task_id)}
    if user_role != "admin":
        query["owner"] = user_email

    result = await tasks_col.delete_one(query)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found or not authorized to delete")

    return {"message": "Task deleted successfully"}
