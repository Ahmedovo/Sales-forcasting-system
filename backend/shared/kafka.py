from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from kafka import KafkaProducer, KafkaConsumer

logger = logging.getLogger(__name__)


@dataclass
class KafkaConfig:
    bootstrap_servers: str
    client_id: str
    group_id: Optional[str] = None

def create_json_producer(config: KafkaConfig) -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=config.bootstrap_servers,
        client_id=config.client_id,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: (k.encode("utf-8") if isinstance(k, str) else k),
        acks="all",
        linger_ms=5,
        retries=5,
    )


def create_json_consumer(config: KafkaConfig, topics: Iterable[str]) -> KafkaConsumer:
    if not config.group_id:
        raise ValueError("group_id is required for consumer")
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=config.bootstrap_servers,
        client_id=config.client_id,
        group_id=config.group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        max_poll_records=200,
    )
    return consumer


def consume_loop(consumer: KafkaConsumer, handler: Callable[[str, dict], None]) -> None:
    for message in consumer:
        try:
            handler(message.key.decode("utf-8") if message.key else None, message.value)
            consumer.commit()
        except Exception as exc:
            logger.exception("Error processing message from topic %s: %s", message.topic, exc)
            # do not commit on error for at-least-once semantics
