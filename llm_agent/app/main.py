from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.ai_service import generate_workflow
from app.db.database import SessionLocal
from app.db.models import Workflow
from pydantic import BaseModel
from contextlib import asynccontextmanager
from app.db.init_db import init_db

# Lifespan handler to initialize DB at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield 

app = FastAPI(title="AI Task Architect", lifespan=lifespan)


# Request schema
class PromptRequest(BaseModel):
    prompt: str


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST /generate → returns and saves generated workflow
@app.post("/generate")
async def generate(request: PromptRequest, db: Session = Depends(get_db)):
    try:
        result = generate_workflow(request.prompt)
        workflow = Workflow(
            name=result["name"],
            prompt=request.prompt,
            workflow_json=result
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
