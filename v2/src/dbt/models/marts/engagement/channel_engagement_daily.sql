with daily as (

    select * from {{ ref('int_chat_features__to_channel_daily') }}

),

final as (

    select
        event_date as date_day,
        channel,

        total_messages,
        unique_chatters,

        case
            when unique_chatters > 0
                then total_messages * 1.0 / unique_chatters
            else null
        end as avg_messages_per_chatter,

        avg_message_length,
        avg_token_count,
        avg_text_complexity_proxy,
        avg_event_to_feature_latency_seconds,

        link_count_sum,
        candidate_emote_token_count_sum,

        repeat_spam_count,
        repeat_spam_rate,

        engagement_signal_count,
        engagement_signal_rate

    from daily

)

select * from final