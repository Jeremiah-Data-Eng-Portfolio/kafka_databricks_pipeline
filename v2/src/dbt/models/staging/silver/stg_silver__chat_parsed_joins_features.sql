with parsed_source as (

    select * from {{ ref('base_silver__chat_parsed') }}

),

parsed_ranked as (

    select
        *,
        row_number() over (
            partition by event_id
            order by
                coalesce(_batch_processed_ts, silver_processed_ts) desc,
                coalesce(_batch_id, -1) desc,
                coalesce(_run_id, '') desc
        ) as row_num
    from parsed_source

),

parsed as (

    select
        event_id,
        source_topic,
        source_partition,
        source_offset,
        event_ts,
        bronze_ingestion_ts,
        silver_processed_ts,
        channel,
        chatter_id,
        message_text,
        message_text_normalized,
        message_length,
        source_platform
    from parsed_ranked
    where row_num = 1

),

features_source as (

    select * from {{ ref('base_silver__chat_features') }}

),

features_ranked as (

    select
        *,
        row_number() over (
            partition by event_id
            order by
                coalesce(_batch_processed_ts, feature_processed_ts) desc,
                coalesce(_batch_id, -1) desc,
                coalesce(_run_id, '') desc
        ) as row_num
    from features_source

),

features as (

    select
        event_id,
        token_count,
        alpha_char_count,
        numeric_char_count,
        link_count,
        candidate_emote_token_count,
        repeat_char_ratio,
        text_complexity_proxy,
        event_to_feature_latency_seconds,
        has_repeat_spam_pattern,
        engagement_signal,
        feature_processed_ts
    from features_ranked
    where row_num = 1

),

joined as (

    select
        p.event_id,
        p.source_topic,
        p.source_partition,
        p.source_offset,
        p.event_ts,
        p.bronze_ingestion_ts,
        p.silver_processed_ts,
        p.channel,
        p.chatter_id,
        p.message_text,
        p.message_text_normalized,
        p.message_length,
        p.source_platform,

        f.token_count,
        f.alpha_char_count,
        f.numeric_char_count,
        f.link_count,
        f.candidate_emote_token_count,
        f.repeat_char_ratio,
        f.text_complexity_proxy,
        f.event_to_feature_latency_seconds,
        f.has_repeat_spam_pattern,
        f.engagement_signal,
        f.feature_processed_ts

    from parsed p
    left join features f
        on p.event_id = f.event_id

)

select * from joined
