
from fastapi import FastAPI

app = FastAPI(title="CampusConnect")


@app.get("/")
def home():
    return {
        "message": "Welcome to CampusConnect!",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}

