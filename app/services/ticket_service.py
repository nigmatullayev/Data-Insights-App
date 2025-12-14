"""
Support Ticket Service
Handles ticket creation and external integrations (GitHub, Trello, Jira)
"""
import os
import json
from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime
from typing import Optional, Dict

class TicketService:
    def __init__(self):
        # External service configurations (can be moved to .env)
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.github_repo = os.getenv("GITHUB_REPO", "")
        self.trello_api_key = os.getenv("TRELLO_API_KEY", "")
        self.jira_url = os.getenv("JIRA_URL", "")
    
    def create_ticket(
        self,
        db: Session,
        title: str,
        description: str,
        priority: str = "medium",
        integrate_with: Optional[str] = None
    ) -> Dict:
        """
        Create a support ticket and optionally integrate with external services
        """
        ticket = models.SupportTicket(
            title=title,
            description=description,
            priority=priority,
            status="open"
        )
        
        db.add(ticket)
        db.flush()  # Get the ID
        
        external_id = None
        external_url = None
        
        # Integrate with external service if requested
        if integrate_with:
            if integrate_with.lower() == "github" and self.github_token and self.github_repo:
                result = self._create_github_issue(title, description)
                if result:
                    external_id = result.get("number")
                    external_url = result.get("html_url")
            elif integrate_with.lower() == "trello" and self.trello_api_key:
                result = self._create_trello_card(title, description)
                if result:
                    external_id = result.get("id")
                    external_url = result.get("url")
            elif integrate_with.lower() == "jira" and self.jira_url:
                result = self._create_jira_issue(title, description)
                if result:
                    external_id = result.get("key")
                    external_url = result.get("self")
        
        if external_id:
            ticket.external_id = str(external_id)
            ticket.external_url = external_url
        
        db.commit()
        db.refresh(ticket)
        
        return {
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "status": ticket.status,
            "priority": ticket.priority,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
            "external_id": ticket.external_id,
            "external_url": ticket.external_url
        }
    
    def _create_github_issue(self, title: str, description: str) -> Optional[Dict]:
        """
        Create GitHub issue (requires GITHUB_TOKEN and GITHUB_REPO)
        """
        try:
            import requests
            
            url = f"https://api.github.com/repos/{self.github_repo}/issues"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {
                "title": title,
                "body": description,
                "labels": ["support-ticket"]
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                return response.json()
        except Exception as e:
            print(f"GitHub integration error: {e}")
        return None
    
    def _create_trello_card(self, title: str, description: str) -> Optional[Dict]:
        """
        Create Trello card (requires TRELLO_API_KEY and TRELLO_TOKEN)
        """
        try:
            import requests
            
            trello_token = os.getenv("TRELLO_TOKEN", "")
            trello_list_id = os.getenv("TRELLO_LIST_ID", "")
            
            if not trello_token or not trello_list_id:
                return None
            
            url = "https://api.trello.com/1/cards"
            params = {
                "key": self.trello_api_key,
                "token": trello_token,
                "idList": trello_list_id,
                "name": title,
                "desc": description
            }
            
            response = requests.post(url, params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Trello integration error: {e}")
        return None
    
    def _create_jira_issue(self, title: str, description: str) -> Optional[Dict]:
        """
        Create Jira issue (requires JIRA_URL, JIRA_EMAIL, JIRA_TOKEN)
        """
        try:
            import requests
            from base64 import b64encode
            
            jira_email = os.getenv("JIRA_EMAIL", "")
            jira_token = os.getenv("JIRA_TOKEN", "")
            jira_project = os.getenv("JIRA_PROJECT", "")
            
            if not jira_email or not jira_token or not jira_project:
                return None
            
            url = f"{self.jira_url}/rest/api/3/issue"
            auth_string = b64encode(f"{jira_email}:{jira_token}".encode()).decode()
            headers = {
                "Authorization": f"Basic {auth_string}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            data = {
                "fields": {
                    "project": {"key": jira_project},
                    "summary": title,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [{"type": "text", "text": description}]
                            }
                        ]
                    },
                    "issuetype": {"name": "Task"}
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                return response.json()
        except Exception as e:
            print(f"Jira integration error: {e}")
        return None
    
    def get_tickets(self, db: Session, status: Optional[str] = None, limit: int = 50):
        """
        Get all tickets, optionally filtered by status
        """
        query = db.query(models.SupportTicket)
        if status:
            query = query.filter(models.SupportTicket.status == status)
        tickets = query.order_by(models.SupportTicket.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "status": ticket.status,
                "priority": ticket.priority,
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "external_id": ticket.external_id,
                "external_url": ticket.external_url
            }
            for ticket in tickets
        ]

