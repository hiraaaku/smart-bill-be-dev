# file: app/api/receipts.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import UUID
from sqlalchemy.orm import Session
from database import SessionLocal
import models  

from fastapi import Path
from fastapi.responses import JSONResponse
from sqlalchemy import text


router = APIRouter()

class OCRUpdateRequest(BaseModel):
    raw_ocr_result: dict  # atau pakai Any kalau perlu fleksibel

# Dependency untuk inject DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/receipts/{receipt_id}")
async def get_receipt_detail(receipt_id: UUID):
    query = text("""
        SELECT id, user_id, image_url, raw_ocr_result, created_at
        FROM receipts
        WHERE id = :receipt_id
    """)
    import database
    with database.engine.connect() as conn:
        result = conn.execute(query, {"receipt_id": str(receipt_id)}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Receipt not found")

    return {
        "id": result.id,
        "user_id": result.user_id,
        "image_url": result.image_url,
        "raw_ocr_result": result.raw_ocr_result,
        "created_at": result.created_at
    }

@router.patch("/receipts/{receipt_id}")
def update_ocr_result(receipt_id: UUID, payload: OCRUpdateRequest, db: Session = Depends(get_db)):
    receipt = db.query(models.Receipt).filter(models.Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    receipt.raw_ocr_result = payload.raw_ocr_result
    db.commit()

    return {"message": "OCR result updated"}
