import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "8467938586:AAG1UDrHvWpgoZ3zI2vw_ranUZjajPoyuh4")
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID", "6123609704")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shop.db")

# Frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# API
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Mini App
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://yourdomain.com/app")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# Debug
DEBUG = os.getenv("DEBUG", "False") == "True"
