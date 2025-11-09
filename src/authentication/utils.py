from sqlalchemy.orm import Session
from ..db.models import Users
from . import schemas
import random
from .dependencies import HashVerifyPassword
from ..error import SQLAlchemyDataCreationError, UsernameExistException


hasher = HashVerifyPassword()


def get_user_by_id(user_id: int, session: Session) -> Users | None:
    user = session.query(Users).filter(Users.user_id == user_id).first()
    return user


def get_user_by_email(email: str, session: Session) -> Users | None:
    user = session.query(Users).filter(Users.email == email).first()
    return user


def get_user_by_username(username: str, session: Session) -> Users | None:
    user = session.query(Users).filter(Users.username == username).first()
    return user


def get_all_users(session: Session) -> list[Users]:
    users = session.query(Users).all()
    return users


def verify_user_email_or_username(
    email_or_username: str, session: Session
) -> Users | None:
    user = get_user_by_email(email=email_or_username, session=session)
    if not user:
        user = get_user_by_username(username=email_or_username, session=session)
    return user


class UsernameGen:
    def __init__(self, session: Session) -> None:
        self.session = session

    def username_exists(self, username) -> bool:
        user = get_user_by_username(username=username, session=self.session)
        if user:
            return True
        else:
            return False

    def auto_username(self, firstname: str, lastname: str) -> str:
        while True:
            num = "".join([str(random.randint(0, 9)) for _ in range(5)])
            symbol = random.choice(["", "-", "_", "."])
            username = firstname.lower() + symbol + lastname.lower() + num
            if not self.username_exists(username=username):
                break
        return username


def create_new_user(user: schemas.UserSignUpModel, session: Session) -> Users:
    user_gen = UsernameGen(session=session)
    username = user_gen.auto_username(user.firstname, user.lastname)
    user = schemas.UserInModel(
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        is_admin=user.is_admin,
        password_hash=hasher.hash_password(user.password),
        username=username,
    )
    try:
        add_user = Users(**user.model_dump())
        session.add(add_user)
        session.commit()
        session.refresh(add_user)
    except Exception as e:
        raise SQLAlchemyDataCreationError(str(e))
    else:
        return add_user


def update_user_profile(
    user_id: int, user_in: schemas.UserUpdateModel, session: Session
) -> Users:
    user_query = session.query(Users).filter(Users.user_id == user_id)
    user = user_query.first()
    user_in.firstname = user_in.firstname if user_in.firstname else user.firstname
    user_in.lastname = user_in.lastname if user_in.lastname else user.lastname
    user_in.dob = user_in.dob if user_in.dob else user.dob
    user_in.image_url = user_in.image_url if user_in.image_url else user.image_url
    if user_in.username:
        username_gen = UsernameGen(session=session)
        username_exist = username_gen.username_exists(user_in.username)
        if username_exist:
            raise UsernameExistException("Username does not exist.")
    else:
        user_in.username = user.username
    try:
        user_query.update(user_in.model_dump())
        session.commit()
    except Exception as e:
        raise SQLAlchemyDataCreationError(str(e))
    else:
        return user
