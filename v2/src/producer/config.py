from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProducerConfig:
    environment: str
    kafka_bootstrap_servers: str
    kafka_raw_topic: str
    kafka_client_id: str
    kafka_security_protocol: str
    kafka_sasl_mechanism: str
    kafka_api_key: str
    kafka_api_secret: str
    twitch_server: str
    twitch_port: int
    twitch_nick: str
    twitch_token: str
    twitch_channel: str
    poll_timeout_seconds: int
    kafka_retries: int
    kafka_retry_backoff_ms: int

    @staticmethod
    def _require(name: str) -> str:
        value = os.getenv(name, "").strip()
        if not value:
            raise ValueError(f"Missing required environment variable: {name}")
        return value

    @staticmethod
    def _int(name: str, default: int) -> int:
        raw = os.getenv(name)
        if raw is None or raw.strip() == "":
            return default
        try:
            return int(raw)
        except ValueError as exc:
            raise ValueError(f"Invalid integer for {name}: {raw}") from exc

    @classmethod
    def from_env(cls) -> "ProducerConfig":
        kafka_security_protocol = os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_SSL").strip()
        kafka_sasl_mechanism = os.getenv("KAFKA_SASL_MECHANISM", "PLAIN").strip()
        api_key = os.getenv("API_KEY", "").strip()
        api_secret = os.getenv("API_SECRET", "").strip()

        if kafka_security_protocol.upper().startswith("SASL"):
            if not api_key:
                raise ValueError("Missing required environment variable: API_KEY")
            if not api_secret:
                raise ValueError("Missing required environment variable: API_SECRET")

        return cls(
            environment=os.getenv("APP_ENV", "dev"),
            kafka_bootstrap_servers=cls._require("KAFKA_BOOTSTRAP_SERVERS"),
            kafka_raw_topic=os.getenv("KAFKA_RAW_TOPIC", "twitch_chat_raw"),
            kafka_client_id=os.getenv("KAFKA_CLIENT_ID", "twitch-raw-producer-v2"),
            kafka_security_protocol=kafka_security_protocol,
            kafka_sasl_mechanism=kafka_sasl_mechanism,
            kafka_api_key=api_key,
            kafka_api_secret=api_secret,
            twitch_server=os.getenv("TWITCH_SERVER", "irc.chat.twitch.tv"),
            twitch_port=cls._int("TWITCH_PORT", 6667),
            twitch_nick=cls._require("TWITCH_NICK"),
            twitch_token=cls._require("TWITCH_TOKEN"),
            twitch_channel=cls._require("TWITCH_CHANNEL"),
            poll_timeout_seconds=cls._int("PRODUCER_POLL_TIMEOUT_SECONDS", 30),
            kafka_retries=cls._int("KAFKA_RETRIES", 10),
            kafka_retry_backoff_ms=cls._int("KAFKA_RETRY_BACKOFF_MS", 500),
        )

    def kafka_options(self) -> dict:
        options = {
            "bootstrap_servers": self.kafka_bootstrap_servers,
            "client_id": self.kafka_client_id,
            "retries": self.kafka_retries,
            "retry_backoff_ms": self.kafka_retry_backoff_ms,
        }
        if self.kafka_security_protocol.upper().startswith("SASL"):
            options.update(
                {
                    "security_protocol": self.kafka_security_protocol,
                    "sasl_mechanism": self.kafka_sasl_mechanism,
                    "sasl_plain_username": self.kafka_api_key,
                    "sasl_plain_password": self.kafka_api_secret,
                }
            )
        return options
