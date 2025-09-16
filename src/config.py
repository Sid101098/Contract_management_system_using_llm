# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Email Configuration (for testing)
EMAIL_CONFIG = {
    'from_email': 'contract-bot@example.com',
    'to_email': 'test@example.com',  # Test email address
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'test@example.com',
    'password': 'test-password'
}

# File paths
VECTOR_STORE_PATH = "./chroma_db"
DOCUMENTS_DIRECTORY = "./documents"
