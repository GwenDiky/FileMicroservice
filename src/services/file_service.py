from io import BytesIO

import aioboto3
import httpx
from fastapi import UploadFile

from src.core.config import settings
from src.exceptions import FileDownloadException
from src.schemas import file_schema


class FileService:
    def __init__(
            self,
            bucket_name: str,
            minio_client: Optional[aioboto3.Session().client] = None,
    ):
        self.minio_client = minio_client or aioboto3.Session().client("s3")
        self.bucket_name = bucket_name

    async def get_file_metadata(
        self, file_name: str, file_type: str
    ) -> file_schema.FileSchema:
        async with self.minio_client as client:
            file_path = await self.get_file_path(file_name, file_type)
            response = await client.head_object(
                Bucket=self.bucket_name, Key=file_path
            )
            file_size = response["ContentLength"]
            file_url = await self.get_file_url(file_name, file_type)

            return file_schema.FileSchema(
                file_name=file_name, file_size=file_size, file_url=file_url
            )

    async def get_file_path(self, file_name: str, file_type: str) -> str:
        file_paths = {
            "task": f"task_files/{file_name}",
            "project": f"project_files/{file_name}",
            "user": f"user_files/{file_name}",
        }
        path = file_paths.get(file_type)
        if not path:
            raise ValueError("Invalid file type specified.")
        return path

    async def upload_file(
        self, file: UploadFile, file_type: str
    ) -> file_schema.FileSchema:
        async with self.minio_client as client:
            file_name = file.filename
            file_path = await self.get_file_path(file_name, file_type)
            await client.upload_fileobj(file, self.bucket_name, file_path)

            file_url = await self.get_file_url(file_name, file_type)

            file_size = file.file.seek(0, 2)
            file.file.seek(0)

            return file_schema.FileSchema(
                file_name=file_name,
                file_size=file_size,
                file_url=file_url.file_url,
            )

    async def download_file(self, source: str, destination: str):
        async with self.minio_client as client:
            await client.download_file(self.bucket_name, source, destination)
            return file_schema.FileDownloadSchema(
                source=source, destination=destination
            )

    async def delete_file(
        self, file_name: str, file_type: str
    ) -> file_schema.FileSchema:
        file_path = await self.get_file_path(file_name, file_type)
        file_metadata = await self.get_file_metadata(file_name, file_type)

        async with self.minio_client as client:
            await client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return file_metadata

    async def get_file_url(
        self, file_name: str, file_type: str
    ) -> file_schema.FileUrlSchema:
        async with self.minio_client as client:
            file_path = await self.get_file_path(file_name, file_type)
            response = await client.head_object(
                Bucket=self.bucket_name, Key=file_path
            )
            file_size = response["ContentLength"]

            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_path},
                ExpiresIn=settings.minio.minio_expiration,
            )
        return file_schema.FileUrlSchema(
            file_name=file_name,
            file_url=url,
            file_size=file_size,
            expiration=settings.minio.minio_expiration,
        )

    async def download_file_from_url(self, file_url: str) -> BytesIO:
        async with httpx.AsyncClient() as client:
            response = await client.get(file_url)
            if response.status_code == 200:
                return BytesIO(response.content)
            raise FileDownloadException
