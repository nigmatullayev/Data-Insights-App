from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import Base, engine
from app.db import models
from app.api.chat import router as chat_router
from app.api.data import router as data_router
from app.api.ticket import router as ticket_router
from app.api.tools import router as tools_router
from app.api.health import router as health_router

app = FastAPI(
    title="Data Insights App",
    description="AI-powered chat application for data insights",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    pass  # Static directory might not exist in some environments

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(data_router, prefix="/api", tags=["Data"])
app.include_router(ticket_router, prefix="/api", tags=["Tickets"])
app.include_router(tools_router, prefix="/api", tags=["Tools"])

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Data Insights API is running",
        "endpoints": {
            "chat": "/api/chat",
            "data_summary": "/api/data/summary",
            "create_ticket": "/api/ticket/create",
            "list_tickets": "/api/ticket/list",
            "tools": "/api/tools",
            "docs": "/docs",
            "frontend": "/static/index.html"
        }
    }