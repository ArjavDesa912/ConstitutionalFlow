
from fastapi import FastAPI
from src.api.routes import constitutional

app = FastAPI()

app.include_router(constitutional.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to ConstitutionalFlow"}
