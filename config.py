from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv()

DEBUG = False

# DEBUG CONFIG
if DEBUG:
    DB_URI = 'postgresql://postgres:jowayo@localhost:5432/rtech'
    DOMAIN_NAME = 'https://conduit-cranial-drizzle.ngrok-free.dev'
    FLW_SECRET_KEY = os.getenv('FLW_TEST_SECRET_KEY')
    
# LIVE CONFIG
else:
    DB_URI_FORMAT = os.getenv('DB_URI_FORMAT')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_URI = DB_URI_FORMAT.format(
        password = quote_plus(DB_PASSWORD)
    )
    DOMAIN_NAME = 'https://rtech-8573733132.us-central1.run.app'
    FLW_SECRET_KEY = os.getenv('FLW_SECRET_KEY')
    

# GENERAL CONFIG
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
JWT_KEY = os.getenv('JWT_KEY')
FLW_SECRET_HASH = os.getenv('FLW_SECRET_HASH')

GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

