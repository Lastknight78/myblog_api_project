from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    DEFAULT_PROFILE_IMAGE: str = os.getenv("DEFAULT_PROFILE_IMAGE")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    DB_URL: str = os.getenv("DB_URL")
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: str = os.getenv("MAIL_FROM")
    MAIL_PORT: int = os.getenv("MAIL_PORT")
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME")
    HOST_SERVER: str = os.getenv("HOST_SERVER")
    PROFILE_IMAGE_FOLDER: str = os.getenv("PROFILE_IMAGE_FOLDER")
    POST_IMAGE_FOLDER: str = os.getenv("POST_IMAGE_FOLDER")
    POST_IMAGE_FOLDER: str = os.getenv("POST_IMAGE_FOLDER")
    PROFLE_IMAGE_FOLDER: str = os.getenv("PROFILE_IMAGE_FOLDER")
    


config = Settings()
