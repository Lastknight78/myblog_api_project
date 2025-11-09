from fastapi import UploadFile
import secrets
from .settings.config import config
from .error import ImageFormatNotSupportedException
from .db.models import ImageMapper
from sqlalchemy.orm import Session
import os


# Initialize Supabase client


async def upload_image(file: UploadFile, folder_name: str, session: Session) -> str:
    """Save image locally and return its accessible URL."""
    
    # validate extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpeg", "jpg", "png", "bmp", "webp", "ico"]:
        raise ImageFormatNotSupportedException(
            "The uploaded file should be one of: jpeg, jpg, png, bmp, webp, ico"
        )

    # generate random filename
    filename = secrets.token_hex(10) + "." + ext

    # folder path
    folder_path = os.path.join(folder_name)
    os.makedirs(folder_path, exist_ok=True)  # create folder if not exists

    # full local path
    file_path = os.path.join(folder_path, filename)

    # save file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # build accessible public URL
    public_url = f"{config.HOST_SERVER}/{file_path.replace(os.sep, '/')}"

    # save in database if needed
    image_record = ImageMapper(
        image_name=filename,
        image_url=public_url,
    )
    session.add(image_record)
    session.commit()
    session.refresh(image_record)

    return public_url


def delete_image(file_path: str):
    """Delete image from local storage."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")
