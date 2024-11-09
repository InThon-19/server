import io
from google.cloud import storage
from config import BUCKET_NAME
from PIL import Image

client = storage.Client()
bucket = client.bucket(BUCKET_NAME)


def resize_and_convert_to_webp(image_bytes: bytes, width: int, height: int) -> bytes:
    webp_io = io.BytesIO()
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.resize((width, height))
        img.save(webp_io, format="webp")
    return webp_io.getvalue()