from fastapi import FastAPI
from app.db.database import Base, engine
from app.db import models
from app.api.chat import router as chat_router
app = FastAPI(title="Data Insights App")
Base.metadata.create_all(bind=engine)

app.include_router(chat_router, prefix="/api")
@app.get("/")
def root():
    return {"status": "ok"}