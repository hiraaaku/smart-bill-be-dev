# firebase_utils.py
import firebase_admin
from firebase_admin import credentials, storage
import uuid
import os

# Inisialisasi Firebase Admin SDK
cred = credentials.Certificate("smart-bill-firebase-service-account-key.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'hira-efata-playground.firebasestorage.app'
})

def upload_image_to_firebase(file_path: str) -> str:
    bucket = storage.bucket()
    filename = f"receipts/{uuid.uuid4().hex}_{os.path.basename(file_path)}"
    blob = bucket.blob(filename)
    
    # Upload file
    blob.upload_from_filename(file_path)
    
    # Generate signed URL (berlaku 1 jam)
    url = blob.generate_signed_url(expiration=3600)
    
    return url