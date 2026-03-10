select
  topic,
  partition,
  offset,
  user,
  message,
  sent_compound,
  message_length,
  entropy,
  is_emote_only,
  repeat_char_ratio,
  engagement_flag,
  kafka_timestamp,
  ingest_ts
from {{ source('silver', 'twitch_chat_parsed') }}
