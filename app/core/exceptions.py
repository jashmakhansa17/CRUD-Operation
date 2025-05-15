from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from .constants import (
    item_not_found_exception,
    item_invalid_data_exception,
    internal_server_exception,
)
from .logers import logger


class ItemNotFoundException(HTTPException):
    def __init__(self, type, item_id=None):
        message = item_not_found_exception(type=type, item_id=item_id)
        logger.warning(message)

        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class ItemInvalidDataException(HTTPException):
    def __init__(self, e: IntegrityError):
        message = item_invalid_data_exception
        logger.warning(e.orig)

        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class InternalServerException(HTTPException):
    def __init__(self, e, file):
        message = internal_server_exception
        log = f"{e} in {file}"
        logger.warning(log)

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        )
