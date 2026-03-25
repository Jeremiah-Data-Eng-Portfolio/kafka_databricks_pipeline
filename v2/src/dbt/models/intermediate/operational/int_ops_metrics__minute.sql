with batch_metrics as (

    select * from {{ ref('stg_ops__batch_metrics') }}

),

normalized as (

    select
        run_id,
        date_trunc('minute', batch_processed_ts) as event_minute,
        job_name as pipeline_stage,
        target_table,
        row_count,
        batch_id,
        batch_processed_ts
    from batch_metrics

),

aggregated as (

    select
        run_id,
        event_minute,
        pipeline_stage,

        count(*) as batch_count,
        sum(case when row_count = 0 then 1 else 0 end) as zero_row_batch_count,

        sum(row_count) as total_rows_written,
        avg(row_count) as avg_rows_per_batch,

        sum(case when target_table like '%bronze_chat_raw' then row_count else 0 end) as bronze_row_count,
        sum(case when target_table like '%silver_chat_parsed' then row_count else 0 end) as valid_event_count,
        sum(case when target_table like '%silver_chat_features' then row_count else 0 end) as feature_row_count,
        sum(case when target_table like '%chat_dlq' then row_count else 0 end) as dlq_row_count_from_sink,

        min(batch_processed_ts) as first_batch_processed_ts,
        max(batch_processed_ts) as last_batch_processed_ts

    from normalized
    group by 1, 2, 3

)

select * from aggregated