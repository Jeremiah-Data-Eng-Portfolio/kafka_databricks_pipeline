with features as (

    select * from {{ ref('stg_silver__chat_parsed_joins_features') }}

),

aggregate_features_to_minute_grain as (

    select
        date_trunc('minute', event_ts) as event_minute,
        channel,
        count(*) as total_messages,
        count(distinct chatter_id) as unique_chatters,

        count(token_count) as feature_enriched_message_count,

        avg(message_length) as avg_message_length,
        avg(token_count) as avg_token_count,
        avg(alpha_char_count) as avg_alpha_char_count,
        avg(numeric_char_count) as avg_numeric_char_count,
        avg(repeat_char_ratio) as avg_repeat_char_ratio,
        avg(text_complexity_proxy) as avg_text_complexity_proxy,
        avg(event_to_feature_latency_seconds) as avg_event_to_feature_latency_seconds,

        sum(link_count) as link_count_sum,
        sum(candidate_emote_token_count) as candidate_emote_token_count_sum,

        sum(case when has_repeat_spam_pattern is true then 1 else 0 end) as repeat_spam_count,
        avg(
            case
                when has_repeat_spam_pattern is true then 1.0
                when has_repeat_spam_pattern is false then 0.0
                else null
            end
        ) as repeat_spam_rate,

        sum(case when engagement_signal is true then 1 else 0 end) as engagement_signal_count,
        avg(
            case
                when engagement_signal is true then 1.0
                when engagement_signal is false then 0.0
                else null
            end
        ) as engagement_signal_rate
    from features
    group by 1, 2

)

select * from aggregate_features_to_minute_grain
