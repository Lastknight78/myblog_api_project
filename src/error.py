from typing import Callable
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class BaseException(Exception):
    pass


class JWTDecodeError(BaseException):
    pass


class InvalidLoginCredentials(BaseException):
    pass


class UserNotActiveError(BaseException):
    pass


class SQLAlchemyDataCreationError(BaseException):
    pass


class UserExistException(BaseException):
    pass


class UserNotFoundException(BaseException):
    pass


class UsernameExistException(BaseException):
    pass


class InvalidEmailVerificationToken(BaseException):
    pass


class ItemNotFoundException(BaseException):
    pass


class OperationNotAllowedException(BaseException):
    pass


class AccountDeactivatedException(BaseException):
    pass


class UserRoleException(BaseException):
    pass


class ImageFormatNotSupportedException(BaseException):
    pass


def create_error_handler(
    status_code: int, error_code: str
) -> Callable[[Request, Exception], JSONResponse]:

    def error_handler(request: Request, exc: BaseException):
        return JSONResponse(
            status_code=status_code,
            content={"message": str(exc), "error_code": error_code},
        )

    return error_handler


def add_error_handlers(app: FastAPI):
    app.add_exception_handler(
        JWTDecodeError,
        handler=create_error_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="jwt_decode_error",
        ),
    )
    app.add_exception_handler(
        ItemNotFoundException,
        handler=create_error_handler(
            status_code=status.HTTP_404_NOT_FOUND, error_code="item_not_found_error"
        ),
    )
    app.add_exception_handler(
        InvalidLoginCredentials,
        handler=create_error_handler(
            status_code=status.HTTP_401_UNAUTHORIZED, error_code="credential_error"
        ),
    )
    app.add_exception_handler(
        AccountDeactivatedException,
        handler=create_error_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="account_deactivated_error",
        ),
    )
    app.add_exception_handler(
        UserNotActiveError,
        handler=create_error_handler(
            status_code=status.HTTP_401_UNAUTHORIZED, error_code="credential_error"
        ),
    )
    app.add_exception_handler(
        SQLAlchemyDataCreationError,
        handler=create_error_handler(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="data_posting_error",
        ),
    )
    app.add_exception_handler(
        ImageFormatNotSupportedException,
        handler=create_error_handler(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="image_format_error",
        ),
    )
    app.add_exception_handler(
        UsernameExistException,
        handler=create_error_handler(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="username_exist_error",
        ),
    )
    app.add_exception_handler(
        UserExistException,
        handler=create_error_handler(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="email_exist_error",
        ),
    )
    app.add_exception_handler(
        UserNotFoundException,
        handler=create_error_handler(
            status_code=status.HTTP_404_NOT_FOUND, error_code="user_not_found_error"
        ),
    )
    app.add_exception_handler(
        InvalidEmailVerificationToken,
        handler=create_error_handler(
            status_code=status.HTTP_400_BAD_REQUEST, error_code="invalid_token_error"
        ),
    )
    app.add_exception_handler(
        OperationNotAllowedException,
        handler=create_error_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="Operation_forbidden_error",
        ),
    )
    app.add_exception_handler(
        UserRoleException,
        handler=create_error_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="enpoint_forbidden_error",
        ),
    )
