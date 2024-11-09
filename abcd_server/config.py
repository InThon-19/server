import os
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")  
BUCKET_NAME = os.getenv("BUCKET_NAME")
CREDENTIALS_PATH = "./credentials.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH