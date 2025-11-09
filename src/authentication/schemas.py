from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginBearerModel(BaseModel):
    access_token: str
    token_type: str


class Payload(BaseModel):
    user_id: int
    is_admin: bool


class EmailTokenOut(BaseModel):
    message: str
    link: dict | None = None


class UserBaseModel(BaseModel):
    email: EmailStr = Field(examples=["johndoe@email.com"])
    firstname: str = Field(examples=["John"])
    lastname: str = Field(examples=["Doe"])
    is_admin: bool = False


class UserInModel(UserBaseModel):
    password_hash: str
    username: str


class UserSignUpModel(UserBaseModel):
    password: str = Field(examples=["secret"], min_length=5)

    @field_validator("email")
    @classmethod
    def email_to_lowercase(cls, v: str):
        return v.lower()

    @field_validator("firstname")
    @classmethod
    def firstname_to_sentence_case(cls, v: str):
        return v.capitalize()

    @field_validator("lastname")
    @classmethod
    def lastname_to_sentence_case(cls, v: str):
        return v.capitalize()


class UserOutModel(UserBaseModel):
    user_id: int
    username: str
    dob: date | None = None
    is_active: bool
    created_at: datetime
    image_url: str

    class ConfigDict:
        from_attributes = True


class UserUpdateModel(BaseModel):
    firstname: str | None = Field(None, examples=["John"])
    lastname: str | None = Field(None, examples=["Doe"])
    username: str | None = Field(None, examples=["johndoe123"])
    dob: date | None = Field(None, examples=["1991-10-11"])
    image_url: str | None = Field(None, examples=["https://profile.png"])
