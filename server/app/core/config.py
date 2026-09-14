import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")
DATABASE_URL = os.getenv("DATABASE_URL")
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
