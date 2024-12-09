import asyncio
import json
import logging

import aiokafka
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from fastapi import UploadFile

logger = logging.getLogger(__name__)


class KafkaConsumer:
    def __init__(
        self,
        minio_client,
        bootstrap_servers="kafka:9092",
        group_id="static-consumer-group",
        topic="static",
    ):
        self.minio_client = minio_client
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topic = topic

    async def consume_messages(self):
        logger.debug(
            "Starting to consume messages from Kafka topic: %s", self.topic
        )

        while True:
            try:
                consumer = AIOKafkaConsumer(
                    self.topic,
                    loop=asyncio.get_event_loop(),
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=self.group_id,
                    auto_offset_reset="earliest",
                )

                await consumer.start()

                async for message in consumer:
                    logger.info(
                        "Consumed message: %s from offset %d",
                        message.value.decode("utf-8"),
                        message.offset,
                    )
                    await self.process_message(message)

            except aiokafka.errors.NotCoordinatorForGroupError:
                logger.error("Coordinator for group not found, retrying...")
                await asyncio.sleep(5)
            except aiokafka.errors.KafkaConnectionError as e:
                logger.error("Connection error: %s, retrying...", e)
                await asyncio.sleep(5)
            finally:
                await consumer.stop()

    async def process_message(self, msg):
        try:
            logger.debug("Starting message processing")
            message = msg.value.decode("utf-8")
            event = json.loads(message)
            logger.info("Processed event: %s", event)

            event_type = event.get("event_type")
            file_data = event.get("file_data")

            if file_data:
                logger.info("Received file_data: %s", file_data)
            else:
                logger.info("Didn't receive file data'")

            file_name = file_data.get("file_name")
            file_type = file_data.get("file_type")
            file_url = file_data.get("file_url")

            if event_type in ["upload_file", "update_file"]:
                file = await self.minio_client.download_file_from_url(file_url)
                upload_file = UploadFile(file=file, filename=file_name)
                await self.minio_client.upload_file(upload_file, file_type)
                logger.info("File successfully uploaded ")

            elif event_type == "delete_file":
                await self.minio_client.delete_file(
                    file_name=file_name, file_type=file_type
                )
                logger.info("File successfully deleted")

        except json.JSONDecodeError as e:
            logger.error("JSON decode error: %s", e)
        except KafkaError as e:
            logger.error("Kafka error: %s", e)
