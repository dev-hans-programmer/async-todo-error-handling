from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors.exceptions import AppError, UserAlreadyExists
from app.errors.responses import ErrorDetail, ErrorResponse

ERROR_STATUS_CODES = {UserAlreadyExists: status.HTTP_409_CONFLICT}


async def app_error_handler(request: Request, exec: AppError) -> JSONResponse:
    status_code = ERROR_STATUS_CODES.get(
        type(exec), status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    response = ErrorResponse(
        error=ErrorDetail(code=exec.code, message=exec.message, details=exec.details)
    )

    return JSONResponse(
        status_code=status_code, content=response.model_dump(mode="json")
    )


async def unexpected_error_handler(request: Request, exc: Exception):
    print(str(exec))

    response = ErrorResponse(
        error=ErrorDetail(code="INTERNAL_SERVER_ERROR", message="Internal server error")
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(mode="json"),
    )


async def validation_error_handler(request: Request, exec: RequestValidationError):
    validation_errors = []

    for error in exec.errors():
        validation_errors.append(
            {
                "location": list(error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    response = ErrorResponse(
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            details=validation_errors,
        )
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=response.model_dump(mode="json"),
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
