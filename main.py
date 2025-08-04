# main.py
from fastapi import FastAPI
from database import Base, engine
import models
from routers import upload
from app.api import receipts


app = FastAPI(title="Split Bill API")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(upload.router, prefix="/api")

app.include_router(receipts.router, prefix="/api", tags=["Receipts"])

