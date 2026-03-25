with ops as (

    select * from {{ ref('int_ops_metrics__minute') }}

),

dlq as (

    select * from {{ ref('int_dlq__minute') }}

),

joined as (

    select
        o.run_id as run_id,
        o.event_minute as minute_ts,
        o.pipeline_stage as pipeline_stage,

        coalesce(o.batch_count, 0) as batch_count,
        coalesce(o.zero_row_batch_count, 0) as zero_row_batch_count,

        coalesce(o.total_rows_written, 0) as total_rows_written,
        coalesce(o.avg_rows_per_batch, 0.0) as avg_rows_per_batch,

        coalesce(o.bronze_row_count, 0) as bronze_row_count,
        coalesce(o.valid_event_count, 0) as valid_event_count,
        coalesce(o.feature_row_count, 0) as feature_row_count,
        coalesce(o.dlq_row_count_from_sink, 0) as dlq_row_count_from_sink,

        coalesce(d.dlq_count, 0) as dlq_count,
        coalesce(d.retryable_dlq_count, 0) as retryable_dlq_count,
        coalesce(d.parse_error_count, 0) as parse_error_count,
        coalesce(d.contract_error_count, 0) as contract_error_count,
        coalesce(d.distinct_error_code_count, 0) as distinct_error_code_count,

        o.first_batch_processed_ts,
        o.last_batch_processed_ts

    from ops o
    left join dlq d
        on o.run_id = d.run_id
       and o.event_minute = d.event_minute
       and o.pipeline_stage = d.pipeline_stage

),

final as (

    select
        run_id,
        minute_ts,
        pipeline_stage,

        batch_count,
        zero_row_batch_count,

        total_rows_written,
        avg_rows_per_batch,

        bronze_row_count,
        valid_event_count,
        feature_row_count,

        dlq_row_count_from_sink,
        dlq_count,
        retryable_dlq_count,
        parse_error_count,
        contract_error_count,
        distinct_error_code_count,

        case
            when (valid_event_count + dlq_count) > 0
                then dlq_count * 1.0 / (valid_event_count + dlq_count)
            else null
        end as dlq_rate,

        first_batch_processed_ts,
        last_batch_processed_ts

    from joined

)

select * from final