from __future__ import annotations

import json
import signal
import socket
import sys
from datetime import datetime, timezone
from typing import Optional

from producer.config import ProducerConfig
from streaming.utils.logging import get_logger

LOGGER = get_logger("producer.twitch_raw")
RUNNING = True


def _handle_signal(_signum: int, _frame: object) -> None:
    global RUNNING
    RUNNING = False


def _parse_privmsg(irc_line: str) -> Optional[tuple[str, str]]:
    if "PRIVMSG" not in irc_line:
        return None

    try:
        username = irc_line.split("!", 1)[0].lstrip(":")
        message = irc_line.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
        return username, message
    except (IndexError, ValueError):
        return None


def build_event_envelope(irc_line: str, cfg: ProducerConfig) -> dict:
    parsed = _parse_privmsg(irc_line)
    username = parsed[0] if parsed else None
    message = parsed[1] if parsed else None

    return {
        "ingestion_ts": datetime.now(timezone.utc).isoformat(),
        "source": {
            "platform": "twitch",
            "protocol": "irc",
            "server": cfg.twitch_server,
            "channel": cfg.twitch_channel,
        },
        "raw": {
            "irc_line": irc_line,
            "username": username,
            "message": message,
        },
        "metadata": {
            "event_kind": "chat_message" if parsed else "non_chat_event",
            "producer_env": cfg.environment,
            "schema_version": "1.0.0",
        },
    }


def _create_twitch_socket(cfg: ProducerConfig) -> socket.socket:
    sock = socket.socket()
    sock.connect((cfg.twitch_server, cfg.twitch_port))
    sock.send(f"PASS {cfg.twitch_token}\n".encode("utf-8"))
    sock.send(f"NICK {cfg.twitch_nick}\n".encode("utf-8"))
    sock.send(f"JOIN {cfg.twitch_channel}\n".encode("utf-8"))
    return sock


def run() -> None:
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    cfg = ProducerConfig.from_env()
    LOGGER.info("starting producer", extra={"context": {"topic": cfg.kafka_raw_topic, "env": cfg.environment}})

    try:
        from kafka import KafkaProducer
    except Exception as exc:
        raise RuntimeError("kafka-python dependency is required to run producer") from exc

    producer = KafkaProducer(
        **cfg.kafka_options(),
        value_serializer=lambda v: json.dumps(v, ensure_ascii=True).encode("utf-8"),
    )

    sock = _create_twitch_socket(cfg)

    try:
        while RUNNING:
            irc_line = sock.recv(4096).decode("utf-8", errors="replace").strip()
            if not irc_line:
                continue

            if irc_line.startswith("PING"):
                sock.send("PONG :tmi.twitch.tv\n".encode("utf-8"))
                continue

            envelope = build_event_envelope(irc_line, cfg)
            producer.send(cfg.kafka_raw_topic, value=envelope)

            LOGGER.info(
                "event_published",
                extra={
                    "context": {
                        "topic": cfg.kafka_raw_topic,
                        "event_kind": envelope["metadata"]["event_kind"],
                        "channel": cfg.twitch_channel,
                    }
                },
            )
    finally:
        try:
            producer.flush(timeout=10)
            producer.close()
        finally:
            sock.close()
            LOGGER.info("producer_stopped", extra={"context": {"topic": cfg.kafka_raw_topic}})


if __name__ == "__main__":
    try:
        run()
    except Exception as err:
        LOGGER.exception("producer_failed", extra={"context": {"error": str(err)}})
        sys.exit(1)
