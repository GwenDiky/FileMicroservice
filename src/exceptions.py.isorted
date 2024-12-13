from fastapi import HTTPException, status


class FileDownloadException(HTTPException):
    def __init__(self) -> None:
        detail = "Failed to download file"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        )
