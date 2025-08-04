# test_upload.py
from firebase_utils import upload_image_to_firebase

if __name__ == "__main__":
    image_path = "test.jpg"  
    url = upload_image_to_firebase(image_path)
    print("Uploaded image URL:", url)
