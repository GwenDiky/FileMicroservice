import logging

from fastapi import Depends
from minio import Minio

from src.core.config import setup_logging
from src.core.kafka_consumer import KafkaConsumer
from src.core.minio import get_minio_client
from src.services.file_service import FileService

setup_logging()
logger = logging.getLogger(__name__)


async def start_listen(client: Minio = Depends(get_minio_client)):
    file_service = FileService(minio_client=client, bucket_name="files")
    kafka_consumer = KafkaConsumer(minio_client=file_service)
    await kafka_consumer.consume_messages()
