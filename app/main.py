from fastapi import FastAPI

app = FastAPI(title="Data Insights App")

@app.get("/")
def root():
    return {"status": "ok"}