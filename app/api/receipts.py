# file: app/api/receipts.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import UUID
from sqlalchemy.orm import Session
from database import SessionLocal
import models  # pastikan model Receipt ada di sini

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

@router.patch("/receipts/{receipt_id}")
def update_ocr_result(receipt_id: UUID, payload: OCRUpdateRequest, db: Session = Depends(get_db)):
    receipt = db.query(models.Receipt).filter(models.Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    receipt.raw_ocr_result = payload.raw_ocr_result
    db.commit()

    return {"message": "OCR result updated"}
