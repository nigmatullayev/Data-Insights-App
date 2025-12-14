from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.agent import chat_with_agent
from app.core.safety import is_dangerous_query
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Chat endpoint with safety checks
    """
    try:
        # Safety check - prevent dangerous queries
        if is_dangerous_query(payload.message):
            raise HTTPException(
                status_code=400,
                detail="Dangerous operations (DELETE, DROP, etc.) are not allowed"
            )
        
        response = chat_with_agent(payload.message, db)
        
        # Check for errors in response
        if "error" in response:
            raise HTTPException(status_code=500, detail=response.get("error"))
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
