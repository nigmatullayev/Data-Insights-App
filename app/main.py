from fastapi import FastAPI
from app.db.database import Base, engine
from app.db import models

app = FastAPI(title="Data Insights App")
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok"}