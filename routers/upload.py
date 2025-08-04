# routers/upload.py
import shutil
import uuid
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Receipt
from firebase_utils import upload_image_to_firebase

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload")
async def upload_receipt_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),  # nanti bisa ganti ke JWT auth
    db: Session = Depends(get_db)
):
    try:
        # Simpan file sementara ke lokal
        temp_path = f"temp_{uuid.uuid4().hex}_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Upload ke Firebase
        image_url = upload_image_to_firebase(temp_path)

        # Simpan ke DB
        receipt = Receipt(
            user_id=user_id,
            image_url=image_url,
            raw_ocr_result=None
        )
        db.add(receipt)
        db.commit()
        db.refresh(receipt)

        # Hapus file lokal
        shutil.os.remove(temp_path)

        return {
            "message": "Upload successful",
            "receipt_id": str(receipt.id),
            "image_url": image_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
