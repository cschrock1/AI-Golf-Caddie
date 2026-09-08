import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")
DATABASE_URL = os.getenv("DATABASE_URL")
GOLF_API_KEY = os.getenv("GOLF_API_KEY")
GOLF_API_BASE_URL = os.getenv("GOLF_API_BASE_URL", "https://golfapi.io/api/v2.3")
if GOLF_API_BASE_URL == "https://api.golfapi.io":
	GOLF_API_BASE_URL = "https://golfapi.io/api/v2.3"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
CORS_ORIGINS = [
	origin.strip()
	for origin in os.getenv(
		"CORS_ORIGINS",
		f"{FRONTEND_URL},http://127.0.0.1:5173"
	).split(",")
	if origin.strip()
]
CORS_ORIGINS.extend([
	"http://localhost",
	"https://localhost",
	"capacitor://localhost",
	"ionic://localhost",
])
