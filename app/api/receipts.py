# file: app/api/receipts.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from db import database  

router = APIRouter()

class OCRUpdateRequest(BaseModel):
    raw_ocr_result: dict  # atau pakai Any jika lebih fleksibel

@router.patch("/receipts/{receipt_id}")
async def update_ocr_result(receipt_id: UUID, payload: OCRUpdateRequest):
    query = """
    UPDATE receipts
    SET raw_ocr_result = :raw_ocr_result
    WHERE id = :receipt_id
    """
    values = {
        "receipt_id": receipt_id,
        "raw_ocr_result": payload.raw_ocr_result,
    }

    result = await database.execute(query=query, values=values)
    if result == 0:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return {"message": "OCR result updated"}
