with parsed as (

    select * from {{ ref('base_silver__chat_parsed') }}

),

features as (

    select * from {{ ref('base_silver__chat_features') }}

),

parsed_freshness as (

    select
        _run_id as run_id,
        date_trunc('minute', coalesce(_batch_processed_ts, silver_processed_ts)) as event_minute,
        coalesce(_job_name, 'silver_parse') as pipeline_stage,

        avg(unix_timestamp(bronze_ingestion_ts) - unix_timestamp(event_ts)) as avg_event_time_to_ingest_lag_seconds,
        avg(unix_timestamp(silver_processed_ts) - unix_timestamp(bronze_ingestion_ts)) as avg_bronze_to_silver_latency_seconds,
        cast(null as double) as avg_event_to_feature_latency_seconds

    from parsed
    where event_ts is not null
      and bronze_ingestion_ts is not null
      and silver_processed_ts is not null
    group by 1, 2, 3

),

feature_freshness as (

    select
        _run_id as run_id,
        date_trunc('minute', coalesce(_batch_processed_ts, feature_processed_ts)) as event_minute,
        coalesce(_job_name, 'silver_features') as pipeline_stage,

        cast(null as double) as avg_event_time_to_ingest_lag_seconds,
        cast(null as double) as avg_bronze_to_silver_latency_seconds,
        avg(event_to_feature_latency_seconds) as avg_event_to_feature_latency_seconds

    from features
    where event_to_feature_latency_seconds is not null
    group by 1, 2, 3

),

unioned as (

    select * from parsed_freshness

    union all

    select * from feature_freshness

)

select * from unioned
