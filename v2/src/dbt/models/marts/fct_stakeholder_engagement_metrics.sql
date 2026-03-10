{{ config(materialized='table') }}

with base as (
  select
    date_trunc('minute', kafka_timestamp) as minute,
    user,
    sent_compound,
    message_length,
    is_emote_only,
    repeat_char_ratio,
    engagement_flag
  from {{ ref('fct_chat_messages') }}
),

per_minute as (
  select
    minute,
    count(*) as total_messages,
    count(distinct user) as active_chatters,
    avg(cast(engagement_flag as int)) as chat_engagement_rate,
    avg(case when sent_compound > 0.05 then 1 else 0 end) as positive_sentiment_share,
    avg(case when sent_compound < -0.05 then 1 else 0 end) as negative_sentiment_share,
    avg(case when repeat_char_ratio >= 0.7 then 1 else 0 end) as spam_risk_rate,
    avg(case when is_emote_only then 1 else 0 end) as emote_intensity_per_minute,
    avg(message_length) as avg_message_length
  from base
  group by 1
)

select
  minute,
  total_messages,
  active_chatters,
  case when active_chatters = 0 then 0 else total_messages * 1.0 / active_chatters end as messages_per_active_chatter,
  chat_engagement_rate,
  positive_sentiment_share,
  negative_sentiment_share,
  spam_risk_rate,
  emote_intensity_per_minute,
  case when spam_risk_rate > 0.20 then 1 else 0 end as moderation_alert_rate
from per_minute
