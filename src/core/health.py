from fastapi import status
from requests import get
from requests.exceptions import ConnectionError

from src.core.config import settings


async def minio_health() -> bool:
    try:
        if (
            get(
                url=f"http://" f"{settings.minio.minio_uri}/minio/health/live"
            ).status_code == status.HTTP_200_OK
        ):
            return True
        return False
    except ConnectionError:
        return False
