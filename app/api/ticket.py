"""
Support Ticket endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.database import get_db
from app.services.ticket_service import TicketService

router = APIRouter()
ticket_service = TicketService()

class TicketCreateRequest(BaseModel):
    title: str
    description: str
    priority: Optional[str] = "medium"
    integrate_with: Optional[str] = None  # github, trello, jira

@router.post("/ticket/create")
def create_ticket(
    request: TicketCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new support ticket
    """
    try:
        # Validate priority
        valid_priorities = ["low", "medium", "high", "urgent"]
        if request.priority not in valid_priorities:
            request.priority = "medium"
        
        # Validate integrate_with
        valid_integrations = ["github", "trello", "jira", None]
        if request.integrate_with and request.integrate_with.lower() not in valid_integrations:
            request.integrate_with = None
        
        ticket = ticket_service.create_ticket(
            db=db,
            title=request.title,
            description=request.description,
            priority=request.priority,
            integrate_with=request.integrate_with
        )
        
        return {
            "success": True,
            "ticket": ticket,
            "message": "Ticket created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")

@router.get("/ticket/list")
def list_tickets(
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List all support tickets
    """
    try:
        tickets = ticket_service.get_tickets(db, status=status, limit=limit)
        return {
            "success": True,
            "count": len(tickets),
            "tickets": tickets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tickets: {str(e)}")

