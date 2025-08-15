# app.py
from flask import Flask, request, jsonify
import google.generativeai as genai
from PIL import Image, ImageEnhance
import io
import os
import uuid
from datetime import datetime

# Import konfigurasi & firebase
from config import GEMINI_API_KEY, FIREBASE_STORAGE_BUCKET
from firebase_service import initialize_firebase, upload_image_to_firebase, save_receipt_to_firestore

app = Flask(__name__)

# Konfigurasi Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Inisialisasi Firebase
initialize_firebase()

# === OPTIMIZED PROMPT UNTUK GEMINI ===
def get_ocr_prompt():
    return """
    Kamu adalah OCR dan parser struk belanja yang sangat akurat.
    Analisis gambar struk berikut dan ekstrak semua informasi penting.

    Format output HARUS dalam JSON seperti di bawah ini.
    Semua field harus ada, isi dengan null jika tidak ditemukan.
    Semua angka harus dalam string dengan 2 desimal (misal: "25000.00").
    Jangan tambahkan penjelasan, hanya JSON.

    FORMAT OUTPUT:
    {
      "items": [
        {
          "name": "Nasi Goreng",
          "price": "25000.00",
          "quantity": "2",
          "total": "50000.00"
        }
      ],
      "store_information": {
        "address": "Jl. Sudirman No. 123, Jakarta",
        "email": "info@restaurant.com",
        "npwp": "12.345.678.9-012.345",
        "phone_number": "+62812345678",
        "store_name": "Restaurant ABC"
      },
      "totals": {
        "change": "5000.00",
        "discount": "0.00",
        "payment": "105000.00",
        "subtotal": "95000.00",
        "tax": {
          "amount": "5000.00",
          "service_charge": "0.00",
          "dpp": "95000.00",
          "name": "PPN",
          "total_tax": "5000.00"
        },
        "total": "100000.00"
      },
      "transaction_information": {
        "date": "02/08/2025",
        "time": "19:30",
        "transaction_id": "TXN123456789"
      }
    }

    Aturan:
    - Semua nilai angka dalam string, format: "12345.00"
    - Tanggal: format DD/MM/YYYY
    - Waktu: format HH:MM
    - Jika tidak ada info, isi dengan null (bukan string kosong)
    - "quantity" dan "price" harus diisi dari item, bukan dari total
    - "tax" → coba deteksi PPN, pajak lain, service charge
    - "payment" → uang yang dibayar
    - "change" → kembalian
    - "subtotal" → sebelum pajak & diskon
    - "total" → total akhir yang dibayar
    - "dpp" → Dasar Pengenaan Pajak (subtotal sebelum pajak)
    - "npwp" → nomor NPWP toko jika ada
    - Pastikan "time" diisi jika ada di struk
    - Pastikan email toko, NPWP, dan alamat lengkap terbaca
    """

# === Preprocessing Gambar untuk Tingkatkan OCR ===
def preprocess_image(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Resize agar tidak terlalu besar (max 1024px)
        img.thumbnail((1024, 1024), Image.LANCZOS)
        
        # Konversi ke grayscale (bantu OCR baca teks)
        img = img.convert("L")
        
        # Tingkatkan kontras
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Simpan ke bytes
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        return buf.getvalue()
    
    except Exception as e:
        raise ValueError(f"Image preprocessing failed: {str(e)}")

# === Route Utama: OCR dari Foto Struk ===
@app.route('/ocr', methods=['POST'])
def ocr_receipt():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']
    filename = file.filename
    if not filename:
        filename = f"receipt_{uuid.uuid4().hex}.jpg"

    # Baca gambar
    image_bytes = file.read()
    
    try:
        # Preprocess gambar
        processed_bytes = preprocess_image(image_bytes)
        img = Image.open(io.BytesIO(processed_bytes))
    except Exception as e:
        return jsonify({"error": f"Invalid image or preprocessing failed: {str(e)}"}), 400

    # Upload ke Firebase Storage
    try:
        image_url = upload_image_to_firebase(processed_bytes, filename)
    except Exception as e:
        return jsonify({"error": f"Failed to upload to Firebase: {str(e)}"}), 500

    # Kirim ke Gemini
    try:
        prompt = get_ocr_prompt()
        response = model.generate_content([prompt, img])
        raw_output = response.text.strip()

        # Bersihkan output (hapus ```json ... ``` jika ada)
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:-3]

        import json
        result = json.loads(raw_output)

        # Validasi struktur dasar
        required_keys = ["items", "store_information", "totals", "transaction_information"]
        for key in required_keys:
            if key not in result:
                result[key] = {}

        # Tambahkan URL gambar
        result["receipt_image_url"] = image_url

        # Simpan ke Firestore (dengan timestamp)
        transaction_id = result["transaction_information"].get("transaction_id") or str(uuid.uuid4())
        try:
            save_receipt_to_firestore(result, transaction_id)
        except Exception as e:
            print(f"Warning: Failed to save to Firestore: {str(e)}")

        # ✅ Hapus field yang tidak bisa di-JSON-kan sebelum kirim ke frontend
        response_result = result.copy()
        response_result.pop('created_at', None)
        response_result.pop('updated_at', None)

        return jsonify(response_result), 200

    except json.JSONDecodeError as e:
        return jsonify({
            "error": "Gemini returned invalid JSON",
            "raw_output": raw_output
        }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Health Check ===
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "OK", "timestamp": datetime.now().isoformat()}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)