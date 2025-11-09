import logging
import secrets
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import EmailStr
from ..settings.config import config
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from . import schemas
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from sqlalchemy.orm import Session
from ..db.models import EmailToken
from ..error import (
    JWTDecodeError,
    SQLAlchemyDataCreationError,
    InvalidEmailVerificationToken,
    UserRoleException,
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def admin_role_checker(current_user: schemas.Payload) -> None:
    if not current_user.is_admin:
        raise UserRoleException("You are not allowed to access this endpoint.")


class HashVerifyPassword:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hash_password: str) -> bool:
        return pwd_context.verify(password, hash_password)


class JWT:
    def __init__(self):
        self.SECRET_KEY = config.SECRET_KEY
        self.ALGORITHM = config.ALGORITHM

    def jwt_encode_payload(self, payload: dict) -> str:
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def jwt_decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        except JWTError as e:
            raise JWTDecodeError(str(e))
        else:
            return payload


jwt_obj = JWT()


def get_current_user(token: str = Depends(oauth_scheme)) -> schemas.Payload:
    payload = jwt_obj.jwt_decode_token(token=token)
    return schemas.Payload(**payload)


async def send_email(email: list[EmailStr], html: str, subject: str) -> None:
    conf = ConnectionConfig(
        MAIL_USERNAME=config.MAIL_USERNAME,
        MAIL_PASSWORD=config.MAIL_PASSWORD,
        MAIL_FROM=config.MAIL_FROM,
        MAIL_PORT=config.MAIL_PORT,
        MAIL_SERVER=config.MAIL_SERVER,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=False,
    )

    fm = FastMail(conf)

    message = MessageSchema(
        subject=subject,
        recipients=email,
        body=html,
        subtype=MessageType.html,
    )
    try:
        await fm.send_message(message)
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class EmailTokenizer:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def generate_token_(n=20) -> str:
        return secrets.token_hex(n)

    def generate_email_token(self, email: str, old_email: str | None = None) -> str:
        token = self.generate_token_()
        if old_email:
            add_token = EmailToken(email=email, token=token, old_email=old_email)
        else:
            add_token = EmailToken(email=email, token=token)
        try:
            self.session.add(add_token)
            self.session.commit()
            self.session.refresh(add_token)
        except Exception as e:
            raise SQLAlchemyDataCreationError(str(e))
        return token

    def verify_email_token(self, token: str) -> None:
        email_token = (
            self.session.query(EmailToken).filter(EmailToken.token == token).first()
        )
        if not email_token:
            raise InvalidEmailVerificationToken()
        email_token.is_verified = True
        self.session.commit()

    def delete_email_token(self, token: str) -> str | tuple[str, str]:
        email_token = (
            self.session.query(EmailToken).filter(EmailToken.token == token).first()
        )
        if not email_token:
            raise InvalidEmailVerificationToken("The token is invalid or has expired.")
        if not email_token.is_verified:
            raise HTTPException(
                status_code=403,
                detail={
                    "message": "Your token is yet to be verified. Check your email for verification link."
                },
            )
        if not email_token.old_email:
            email = email_token.email
            self.session.delete(email_token)
            self.session.commit()
            return email
        else:
            email = email_token.email
            old_email = email_token.old_email
            self.session.delete(email_token)
            self.session.commit()
            return email, old_email
