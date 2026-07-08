from fastapi import Request
from fastapi.responses import JSONResponse

from core.exceptions import ApplicationException


async def application_exception_handler(
    request: Request,
    exc: ApplicationException
):

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message
        }
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
):

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": str(exc)
        }
    )