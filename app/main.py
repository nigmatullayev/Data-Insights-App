from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
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

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers (before static files to avoid conflicts)
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(data_router, prefix="/api", tags=["Data"])
app.include_router(ticket_router, prefix="/api", tags=["Tickets"])
app.include_router(tools_router, prefix="/api", tags=["Tools"])

# Serve static files (CSS, JS, images)
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root path
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the frontend interface at root path"""
    index_path = Path("static/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return HTMLResponse(content="""
        <html>
            <head><title>Data Insights App</title></head>
            <body>
                <h1>Data Insights API</h1>
                <p>Frontend files not found. Please ensure static/index.html exists.</p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """)

# API info endpoint
@app.get("/api/info")
def api_info():
    """API information endpoint"""
    return {
        "status": "ok",
        "message": "Data Insights API is running",
        "endpoints": {
            "chat": "/api/chat",
            "data_summary": "/api/data/summary",
            "create_ticket": "/api/ticket/create",
            "list_tickets": "/api/ticket/list",
            "tools": "/api/tools",
            "health": "/api/health",
            "docs": "/docs"
        }
    }