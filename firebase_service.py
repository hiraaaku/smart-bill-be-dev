# firebase_service.py
import firebase_admin
from firebase_admin import credentials, storage, firestore
import os
import uuid
from urllib.parse import quote

# Inisialisasi Firebase (hanya sekali)
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
        firebase_admin.initialize_app(cred, {
            'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
        })

# Upload gambar ke Firebase Storage, return public URL
def upload_image_to_firebase(image_bytes, filename):
    bucket = storage.bucket()
    blob = bucket.blob(f"receipts/{filename}")

    # Generate token agar bisa pakai ?token=...
    download_token = str(uuid.uuid4())
    blob.metadata = {
        "firebaseStorageDownloadTokens": download_token
    }

    # Upload file
    blob.upload_from_string(image_bytes, content_type='image/jpeg')

    # Buat URL public
    encoded_path = quote(f"receipts/{filename}")
    bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")
    public_url = f"https://firebasestorage.googleapis.com/v0/b/{bucket_name}/o/{encoded_path}?alt=media&token={download_token}"

    return public_url

# Simpan hasil OCR ke Firestore (dengan timestamp)
def save_receipt_to_firestore(receipt_data, transaction_id):
    db = firestore.client()
    doc_ref = db.collection('receipts').document(transaction_id)
    
    receipt_data['created_at'] = firestore.SERVER_TIMESTAMP
    receipt_data['updated_at'] = firestore.SERVER_TIMESTAMP

    doc_ref.set(receipt_data, merge=True)
    return doc_ref.path