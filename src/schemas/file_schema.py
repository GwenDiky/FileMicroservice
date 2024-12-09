from pydantic import BaseModel


class FileSchema(BaseModel):
    file_name: str
    file_size: int
    file_url: str


class FileDownloadSchema(BaseModel):
    source: str
    destination: str


class FileUrlSchema(FileSchema):
    expiration: int
