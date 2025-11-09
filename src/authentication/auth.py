from datetime import date
from fastapi import BackgroundTasks, Body, Depends, APIRouter, File, Form, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from ..settings.config import config
from ..db.database import get_session
from . import schemas, utils
from sqlalchemy.orm import Session
from .html import verification_email_html, activate_account_html
from ..processor_image import delete_image, upload_image
from ..error import (
    InvalidLoginCredentials,
    UserExistException,
    UserNotActiveError,
    UserNotFoundException,
    AccountDeactivatedException,
)
from .dependencies import (
    JWT,
    HashVerifyPassword,
    get_current_user,
    send_email,
    EmailTokenizer,
    admin_role_checker,
)


jwt = JWT()
hash_verify_pwd = HashVerifyPassword()
auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/login/", response_model=schemas.LoginBearerModel, status_code=200)
def login(
    formdata: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = utils.verify_user_email_or_username(
        email_or_username=formdata.username, session=session
    )
    if not user:
        raise InvalidLoginCredentials(
            "Login fail. Check your username, email, or password."
        )
    if not user.is_active:
        raise UserNotActiveError(
            "User is not yet activated. Check your email for activation link or try to reactive your account."
        )
    if user.acct_deactivated:
        raise AccountDeactivatedException(
            "Your account has been deactivated by the admin."
        )
    hash_password = user.password_hash
    if not hash_verify_pwd.verify_password(formdata.password, hash_password):
        raise InvalidLoginCredentials(
            "Login fail. Check your username, email, or password."
        )
    payload = schemas.Payload(user_id=user.user_id, is_admin=user.is_admin)
    token = jwt.jwt_encode_payload(payload=payload.model_dump())
    return {"access_token": token, "token_type": "bearer"}


@auth_router.post("/signup/", response_model=schemas.EmailTokenOut, status_code=201)
def signup(
    user: schemas.UserSignUpModel,
    background_task: BackgroundTasks,
    session: Session = Depends(get_session),
):
    user_exist = utils.get_user_by_email(email=user.email, session=session)
    if user_exist:
        raise UserExistException("User with this email already exists.")
    user = utils.create_new_user(user=user, session=session)
    email_tokenizer = EmailTokenizer(session)
    token = email_tokenizer.generate_email_token(user.email)
    activation_link = f"http://{config.HOST_SERVER}/api/auth/activate-account/{token}"
    html, subject = activate_account_html(user, activation_link)
    background_task.add_task(send_email, [user.email], html, subject)
    return {
        "message": "Check your email to activate your account.",
        "link": {"activation_link": activation_link},
    }


@auth_router.get("/activate-account/{token}", response_model=schemas.EmailTokenOut)
def activate_account(token: str, session: Session = Depends(get_session)):
    email_tokenizer = EmailTokenizer(session)
    email_tokenizer.verify_email_token(token)
    email = email_tokenizer.delete_email_token(token)
    user = utils.get_user_by_email(email, session)
    user.is_active = True
    session.commit()
    return {"message": "Account successfully activated."}


@auth_router.get("/users/profile/", response_model=schemas.UserOutModel)
def get_current_user_profile(
    current_user: schemas.Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = utils.get_user_by_id(current_user.user_id, session)
    return user


@auth_router.put(
    "/users/update-profile/", response_model=schemas.UserOutModel, status_code=201
)
async def update_user_profile(
    firstname: str | None = Form(None, examples=["John"]),
    lastname: str | None = Form(None, examples=["Doe"]),
    username: str | None = Form(None, examples=["johndoe123"]),
    dob: date | None = Form(None, examples=["1991-10-11"]),
    profile_image: UploadFile | None = File(None),
    current_user: schemas.Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_id = current_user.user_id
    user = utils.get_user_by_id(user_id, session)
    if profile_image:
        folder_name = config.PROFLE_IMAGE_FOLDER
        image_url = await upload_image(profile_image, folder_name, session)
        if user.image_url != config.DEFAULT_PROFILE_IMAGE:
            delete_image(user.image_url, session)
    else:
        image_url = user.image_url

    user_in = schemas.UserUpdateModel(
        firstname=firstname,
        lastname=lastname,
        username=username,
        dob=dob,
        image_url=image_url,
    )
    user = utils.update_user_profile(user_id=user_id, user_in=user_in, session=session)
    return user


@auth_router.post(
    "/users/forget-password/{email}/",
    response_model=schemas.EmailTokenOut,
    status_code=201,
)
async def forget_password(
    email: EmailStr,
    background_task: BackgroundTasks,
    session: Session = Depends(get_session),
):
    user = utils.get_user_by_email(email=email, session=session)
    if not user:
        raise UserNotFoundException(f"User with email {email} cannot be found.")
    email_tokenizer = EmailTokenizer(session=session)
    token = email_tokenizer.generate_email_token(email)
    reset_link = (
        f"http://{config.HOST_SERVER}/api/auth/reset-password/verify-token/{token}/"
    )
    html, subject = verification_email_html(user, reset_link)
    background_task.add_task(send_email, [email], html, subject)
    return {
        "message": "Check your email to reset your password",
        "link": {"reset_link": reset_link},
    }


@auth_router.get(
    "/reset-password/verify-token/{token}/", response_model=schemas.EmailTokenOut
)
def verify_password(token: str, session: Session = Depends(get_session)):
    email_tokenizer = EmailTokenizer(session=session)
    email_tokenizer.verify_email_token(token)
    return {
        "message": f"Reset password token is succcessfully verified. Proceed to 'http://{config.HOST_SERVER}/api/auth/reset-password/update-password/{token}/' to update your password."
    }


@auth_router.post(
    "/reset-password/update-password/{token}/",
    response_model=schemas.EmailTokenOut,
    status_code=201,
)
def update_password(
    token: str, new_password: str = Form(), session: Session = Depends(get_session)
):
    email_tokenizer = EmailTokenizer(session=session)
    email = email_tokenizer.delete_email_token(token)
    user = utils.get_user_by_email(email=email, session=session)
    user.password_hash = hash_verify_pwd.hash_password(new_password)
    session.commit()
    return {"message": "Password updated successfully."}


@auth_router.post(
    "/users/change-email/{new_email}/",
    response_model=schemas.EmailTokenOut,
    status_code=201,
)
def send_update_email_link(
    new_email: EmailStr,
    background_task: BackgroundTasks,
    current_user: schemas.Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = utils.get_user_by_id(current_user.user_id, session)
    email_tokenizer = EmailTokenizer(session=session)
    token = email_tokenizer.generate_email_token(email=new_email, old_email=user.email)
    reset_link = (
        f"http://{config.HOST_SERVER}/api/auth/update-email/verify-token/{token}/"
    )
    html, subject = verification_email_html(user, reset_link)
    background_task.add_task(send_email, [new_email], html, subject)
    return {
        "message": f"Check your email {new_email} for the reset email link.",
        "link": {"reset_link": reset_link},
    }


@auth_router.get("/update-email/verify-token/{token}/")
def update_email(token: str, session: Session = Depends(get_session)):
    email_tokenizer = EmailTokenizer(session=session)
    email_tokenizer.verify_email_token(token)
    new_email, old_email = email_tokenizer.delete_email_token(token)
    user = utils.get_user_by_email(email=old_email, session=session)
    user.email = new_email
    session.commit()
    return {"message": "email changed successfully."}


@auth_router.post("/change-password/{new_password}/")
def change_password(
    new_password: str,
    current_user: schemas.Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = utils.get_user_by_id(current_user.user_id, session)
    user.password_hash = hash_verify_pwd.hash_password(new_password)
    session.commit()
    return {"message": "Password changed successfully."}


@auth_router.get("/all-users/", response_model=list[schemas.UserOutModel])
def get_users(
    session: Session = Depends(get_session),
    current_user: schemas.Payload = Depends(get_current_user),
):
    admin_role_checker(current_user)
    users = utils.get_all_users(session=session)
    return users


@auth_router.get("/users/{user_id}/deactivate/")
def deactivate_user(
    user_id: int,
    current_user: schemas.Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    admin_role_checker(current_user)
    user = utils.get_user_by_id(user_id, session)
    if not user:
        raise UserNotFoundException(f"User with id {user_id} cannot be found")
    user.acct_deactivated = True
    return {"message": f"The user with id {user_id} has been successfully deactivated"}


@auth_router.get("/users/{user_id}/reactivate")
def reactivate_user(
    user_id: int,
    current_user: schemas.Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    admin_role_checker(current_user)
    user = utils.get_user_by_id(user_id, session)
    if not user:
        raise UserNotFoundException(f"User with id {user_id} cannot be found")
    user.acct_deactivated = False
    return {"message": f"The user with id {user_id} has been successfully reactivated"}


@auth_router.delete("/users/")
def delete_user_by_email(
    email: str = Body(),
    current_user: schemas.Payload = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    admin_role_checker(current_user)
    user = utils.get_user_by_email(email=email, session=session)
    if user:
        session.delete(user)
        session.commit()
        return JSONResponse(
            content={"messge": "user deleted successfully"}, status_code=204
        )
    return JSONResponse(content={"message": "user not found"}, status_code=404)


# @auth_router.post("/send-sample-email/")
# async def send_sample_email(email: list[EmailStr] = Body()):
#     html = """
#         <h1>This is a sample message</h1>
#     """
#     subject = "MyBlog - Sample Email"
#     await send_email(email=email, subject=subject, html=html)
#     return {"message": "Email sent successfully"}
