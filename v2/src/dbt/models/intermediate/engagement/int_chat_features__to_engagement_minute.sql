with features as (

    select * from {{ ref('stg_silver__chat_parsed_joins_features') }}

),

aggregate_features_to_minute_grain as (

    select
        date_trunc('minute', event_ts) as event_minute,
        channel,
        count(*) as total_messages,
        count(distinct chatter_id) as unique_chatters,
        avg(message_length) as avg_message_length,
        avg(token_count) as avg_token_count,
        sum(candidate_emote_token_count) as candidate_emote_token_count_sum,
        sum(case when engagement_signal then 1 else 0 end) as engagement_signal_count,
        avg(case when engagement_signal then 1.0 else 0.0 end) as engagement_signal_rate,
        sum(link_count) as link_count_sum,
        sum(case when has_repeat_spam_pattern then 1 else 0 end) as repeat_spam_count,
        avg(case when has_repeat_spam_pattern then 1.0 else 0.0 end) as repeat_spam_rate
    from features
    group by 1, 2

)

select * from aggregate_features_to_minute_grain