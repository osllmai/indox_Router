#!/usr/bin/env python
# Example API with authentication

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from indoxRouter.utils.auth import AuthManager

# Create an instance of the AuthManager
auth_manager = AuthManager()

# Create a FastAPI app
app = FastAPI(title="IndoxRouter API Example")

# Create some example users
admin_id, admin_key = auth_manager.create_user(
    email="admin@example.com", name="Admin User", initial_balance=1000.0
)

user_id, user_key = auth_manager.create_user(
    email="user@example.com", name="Regular User", initial_balance=10.0
)

print(f"Admin API Key: {admin_key}")
print(f"User API Key: {user_key}")


# Models
class UserCreate(BaseModel):
    email: str
    name: str
    initial_balance: float = 0.0


class CreditUpdate(BaseModel):
    user_id: str
    amount: float


class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int = 100


# Dependency for authentication
async def get_current_user(x_api_key: str = Header(...)):
    user = auth_manager.authenticate_user(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user


# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to IndoxRouter API Example"}


@app.post("/users")
async def create_user(
    user_data: UserCreate, current_user: Dict = Depends(get_current_user)
):
    # Only admin can create users (simple example)
    if current_user["email"] != "admin@example.com":
        raise HTTPException(status_code=403, detail="Not authorized to create users")

    user_id, api_key = auth_manager.create_user(
        email=user_data.email,
        name=user_data.name,
        initial_balance=user_data.initial_balance,
    )

    return {
        "user_id": user_id,
        "api_key": api_key,
        "message": "User created successfully",
    }


@app.get("/users/me")
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    return current_user


@app.get("/users")
async def list_users(current_user: Dict = Depends(get_current_user)):
    # Only admin can list users
    if current_user["email"] != "admin@example.com":
        raise HTTPException(status_code=403, detail="Not authorized to list users")

    return auth_manager.list_users()


@app.post("/credits/add")
async def add_credits(
    credit_data: CreditUpdate, current_user: Dict = Depends(get_current_user)
):
    # Only admin can add credits
    if current_user["email"] != "admin@example.com":
        raise HTTPException(status_code=403, detail="Not authorized to add credits")

    success = auth_manager.add_credits(credit_data.user_id, credit_data.amount)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    user = auth_manager.get_user_by_id(credit_data.user_id)
    return {
        "user_id": credit_data.user_id,
        "new_balance": user["balance"],
        "message": f"Added {credit_data.amount} credits successfully",
    }


@app.post("/completions")
async def create_completion(
    request: CompletionRequest, current_user: Dict = Depends(get_current_user)
):
    # Simulate a completion request

    # Calculate cost (simplified example)
    prompt_tokens = len(request.prompt.split())
    completion_tokens = request.max_tokens
    cost_per_token = 0.0001  # Example cost
    estimated_cost = (prompt_tokens + completion_tokens) * cost_per_token

    # Check if user has enough credits
    if current_user["balance"] < estimated_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Required: {estimated_cost}, Available: {current_user['balance']}",
        )

    # Simulate completion (in a real app, you would call the LLM provider here)
    completion_text = (
        f"This is a simulated completion for the prompt: {request.prompt[:20]}..."
    )

    # Deduct credits
    auth_manager.deduct_credits(current_user["id"], estimated_cost)

    # Get updated user data
    updated_user = auth_manager.get_user_by_id(current_user["id"])

    return {
        "text": completion_text,
        "model": request.model,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
        "cost": estimated_cost,
        "remaining_credits": updated_user["balance"],
    }


if __name__ == "__main__":
    import uvicorn
    import platform

    # Check if running on Windows
    if platform.system() == "Windows":
        # On Windows, run without uvloop
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # On Unix systems, can use uvloop for better performance
        uvicorn.run(app, host="0.0.0.0", port=8000, loop="uvloop")
