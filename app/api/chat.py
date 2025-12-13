from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.agent import chat_with_agent

router = APIRouter()

@router.post("/chat")
def chat(payload: dict, db: Session = Depends(get_db)):
    return chat_with_agent(payload["message"], db)
