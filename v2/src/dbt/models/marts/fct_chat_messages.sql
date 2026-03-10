{{ config(materialized='table') }}

select
  {{ dbt_utils.generate_surrogate_key(['topic', 'partition', 'offset']) }} as message_id,
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
from {{ ref('stg_twitch_chat_events') }}
