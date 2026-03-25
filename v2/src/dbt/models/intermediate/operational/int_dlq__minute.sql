with dlq as (

    select * from {{ ref('stg_silver__chat_dlq') }}

),

normalized as (

    select
        _run_id as run_id,
        date_trunc('minute', dlq_ingestion_ts) as event_minute,
        pipeline_stage,
        error_category,
        error_code,
        retryable
    from dlq

),

aggregated as (

    select
        run_id,
        event_minute,
        pipeline_stage,

        count(*) as dlq_count,
        sum(case when retryable then 1 else 0 end) as retryable_dlq_count,

        sum(case when error_category = 'PARSE_ERROR' then 1 else 0 end) as parse_error_count,
        sum(case when error_category = 'CONTRACT_ERROR' then 1 else 0 end) as contract_error_count,

        count(distinct error_code) as distinct_error_code_count

    from normalized
    group by 1, 2, 3

)

select * from aggregated