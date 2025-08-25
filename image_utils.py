# image_utils.py
from PIL import Image
import os
import io

def compress_image(image_bytes, max_size_mb=1.0):
    """
    Compress image bytes to ensure size < max_size_mb.
    Returns compressed image bytes in JPEG format.
    """
    # Baca dari bytes
    img = Image.open(io.BytesIO(image_bytes))

    # Konversi ke RGB jika PNG/RGBA
    if img.mode in ("RGBA", "LA"):
        img = img.convert("RGB")

    # Resize ke ukuran maksimal 1200x1200
    max_dim = 1200
    if img.width > max_dim or img.height > max_dim:
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    # Simpan ke buffer dengan kompresi tinggi
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)

    # Cek ukuran hasil
    compressed_bytes = buf.getvalue()
    if len(compressed_bytes) > max_size_mb * 1024 * 1024:
        # Jika masih terlalu besar, turunkan kualitas
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=70, optimize=True)
        compressed_bytes = buf.getvalue()

    return compressed_bytes