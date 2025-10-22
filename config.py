import os
from dotenv import load_dotenv

load_dotenv()

LLM_HOST = "http://72.56.73.14:8001"

PREDICT_BODY_TYPE_ML_URL = "http://ml:8000/predict_body_type"
# PREDICT_BODY_TYPE_LLM_URL = "http://llm:8001/recommend" # для локального запуска и запуска в докере
PREDICT_BODY_TYPE_LLM_URL = f"{LLM_HOST}/recommend" # для работы на сервере, перед отправкой на гит раскоментируй эту строку


PREDICT_COLOR_TYPE_URL = "http://ml:8000/predict_color_type"
# PREDICT_COLOR_TYPE_LLM_URL = "http://llm:8001/recommend_by_color_type" # для локального запуска и запуска в докере
PREDICT_COLOR_TYPE_LLM_URL = f"{LLM_HOST}/recommend_by_color_type" # для работы на сервере, перед отправкой на гит раскоментируй эту строку

PARSER_URL = "http://parser:8002/parser"

GENERATE_AVATAR_URL = "http://ml:8000/generate-avatar_leonardo"

DATABASE_URL=f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
MONGO_URL="mongodb://mongo:27017"
SECRET_KEY = os.getenv("SECRET_KEY")
MONGO_DB = os.getenv("MONGO_DB")

SHARED_TMP_DIR = "/app/tmp"
