with joined as (

    select * from {{ ref('stg_silver__chat_parsed_joins_features') }}

),

aggregated as (

    select
        _run_id as run_id,
        date_trunc('minute', event_ts) as event_minute,
        pipeline_stage,

        avg(unix_timestamp(bronze_ingestion_ts) - unix_timestamp(event_ts)) as avg_event_time_to_ingest_lag_seconds,
        avg(unix_timestamp(silver_processed_ts) - unix_timestamp(bronze_ingestion_ts)) as avg_bronze_to_silver_latency_seconds,
        avg(
            case
                when pipeline_stage = 'silver_features' then event_to_feature_latency_seconds
                else null
            end
            ) as avg_event_to_feature_latency_seconds

    from joined
    group by 1, 2, 3

)

select * from aggregated