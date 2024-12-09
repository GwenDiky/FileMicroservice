import logging
import sys

from pydantic_settings import BaseSettings

class MinioSettings(BaseSettings):
    minio_root_user: str
    minio_root_password: str
    minio_host: str
    minio_port: int
    minio_secure: bool
    minio_bucket_name: str
    minio_uri: str


class Settings(BaseSettings):
    minio: MinioSettings = MinioSettings()


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)


settings = Settings()
