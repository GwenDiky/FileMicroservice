from minio import Minio
from src.core.config import settings

client = Minio(
    settings.minio.minio_uri,
    access_key=settings.minio.minio_root_user,
    secret_key=settings.minio.minio_root_password,
    secure=settings.minio.minio_secure
)
