import aioboto3
from fastapi import UploadFile

from src.core.config import settings
from src.schemas import file_schema


class FileService:
    def __init__(
        self, minio_client: aioboto3.Session().client, bucket_name: str
    ):
        self.minio_client = minio_client
        self.bucket_name = bucket_name

    async def get_file_metadata(
        self, file_name: str
    ) -> file_schema.FileSchema:
        async with self.minio_client as client:
            response = await client.head_object(
                Bucket=self.bucket_name, Key=file_name
            )
            file_size = response["ContentLength"]
            file_url = await self.get_file_url(file_name)

            return file_schema.FileSchema(
                file_name=file_name, file_size=file_size, file_url=file_url
            )

    async def upload_file(self, file: UploadFile) -> file_schema.FileSchema:
        async with self.minio_client as client:
            file_name = file.filename
            await client.upload_fileobj(file, self.bucket_name, file_name)
            file_url = await self.get_file_url(file_name)

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

    async def delete_file(self, file_name: str) -> file_schema.FileSchema:
        file_metadata = await self.get_file_metadata(file_name)

        async with self.minio_client as client:
            await client.delete_object(Bucket=self.bucket_name, Key=file_name)
            return file_metadata

    async def get_file_url(self, file_name: str) -> file_schema.FileUrlSchema:
        async with self.minio_client as client:
            response = await client.head_object(
                Bucket=self.bucket_name, Key=file_name
            )
            file_size = response["ContentLength"]

            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_name},
                ExpiresIn=settings.minio.minio_expiration,
            )
        return file_schema.FileUrlSchema(
            file_name=file_name,
            file_url=url,
            file_size=file_size,
            expiration=settings.minio.minio_expiration,
        )
