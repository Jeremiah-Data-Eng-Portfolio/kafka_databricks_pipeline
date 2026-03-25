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

        feature_enriched_message_count,
        case
            when total_messages > 0
                then feature_enriched_message_count * 1.0 / total_messages
            else null
        end as feature_enrichment_rate,

        avg_message_length,
        avg_token_count,
        avg_alpha_char_count,
        avg_numeric_char_count,
        avg_repeat_char_ratio,
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
