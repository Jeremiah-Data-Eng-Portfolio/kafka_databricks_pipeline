# So-What Metrics

The v2 Gold layer is designed to answer two kinds of downstream questions:

1. **Channel engagement outcomes** — how active, healthy, and signal-rich chat is over time
2. **Pipeline health outcomes** — how reliably the streaming pipeline is processing valid events and isolating failures

## Primary Gold Models

- `mart_channel_engagement_minute`
- `mart_channel_engagement_daily`
- `mart_pipeline_health_minute`

## Core Metrics

### Channel engagement (minute grain)
- `total_messages`
- `unique_chatters`
- `messages_per_active_chatter`
- `avg_message_length`
- `avg_token_count`
- `link_count_sum`
- `candidate_emote_token_count_sum`
- `repeat_spam_count`
- `repeat_spam_rate`
- `engagement_signal_count`
- `engagement_signal_rate`

### Channel engagement (daily grain)
- `total_messages`
- `unique_chatters`
- `avg_messages_per_chatter`
- `avg_message_length`
- `avg_token_count`
- `avg_text_complexity_proxy`
- `link_count_sum`
- `candidate_emote_token_count_sum`
- `repeat_spam_count`
- `repeat_spam_rate`
- `engagement_signal_count`
- `engagement_signal_rate`

### Pipeline health (minute grain)
- `batch_count`
- `zero_row_batch_count`
- `total_rows_written`
- `avg_rows_per_batch`
- `bronze_row_count`
- `valid_event_count`
- `feature_row_count`
- `dlq_count`
- `dlq_rate`
- `retryable_dlq_count`
- `parse_error_count`
- `contract_error_count`

## Business Questions Supported

### Creator / community questions
- When is chat activity strongest at the channel-minute level?
- Are bursts driven by more unique chatters or by repeated low-signal chatter?
- Is engagement staying healthy over the course of a stream day?
- Are links, repetitive messages, or low-quality patterns increasing during certain periods?

### Operational / platform questions
- Is the pipeline writing valid events consistently at each stage?
- When are DLQ events appearing, and are they parse failures or contract failures?
- Are there zero-row batches or unusual batch patterns that suggest orchestration or upstream issues?
- Is the system producing downstream-ready feature data without malformed events contaminating the valid path?

## Why These Metrics Matter

The Gold layer is intentionally lean.

- The **engagement marts** convert event-level parsed/features data into channel-level rollups that are easier to chart and reason about.
- The **pipeline health mart** converts batch telemetry and DLQ records into operational monitoring metrics that support debugging, reliability reviews, and benchmark interpretation.

Together, these models show both sides of the project:

- a streaming pipeline that is operationally observable
- and a set of curated downstream tables that turn raw event flow into stakeholder-facing analytics