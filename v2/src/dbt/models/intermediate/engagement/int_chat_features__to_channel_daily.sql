with features as (

    select * from {{ ref('stg_silver__chat_parsed_joins_features') }}

),

aggregate_features_to_day_grain as (

    select
        date_trunc('day', event_ts) as event_date,
        channel,
        count(*) as total_messages,
        count(distinct chatter_id) as unique_chatters,
        avg(message_length) as avg_message_length,
        avg(token_count) as avg_token_count,
        avg(alpha_char_count) as avg_alpha_char_count,
        avg(numeric_char_count) as avg_numeric_char_count,
        sum(link_count) as link_count_sum,
        sum(candidate_emote_token_count) as candidate_emote_token_count_sum,
        avg(repeat_char_ratio) as avg_repeat_char_ratio,
        avg(text_complexity_proxy) as avg_text_complexity_proxy,
        avg(event_to_feature_latency_seconds) as avg_event_to_feature_latency_seconds,
        sum(case when has_repeat_spam_pattern then 1 else 0 end) as repeat_spam_count,
        avg(case when has_repeat_spam_pattern then 1.0 else 0.0 end) as repeat_spam_rate,
        sum(case when engagement_signal then 1 else 0 end) as engagement_signal_count,
        avg(case when engagement_signal then 1.0 else 0.0 end) as engagement_signal_rate
    from features
    group by 1, 2

)

select * from aggregate_features_to_day_grain