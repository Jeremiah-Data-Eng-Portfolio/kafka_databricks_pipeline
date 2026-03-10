{{ config(materialized='table') }}

select
  date_trunc('minute', kafka_timestamp) as minute,
  count(*) as message_count,
  avg(sent_compound) as avg_sentiment,
  avg(cast(engagement_flag as int)) as engagement_rate
from {{ ref('fct_chat_messages') }}
group by 1
