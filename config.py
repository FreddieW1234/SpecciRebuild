import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
DEBUG = FLASK_ENV == 'development'
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
