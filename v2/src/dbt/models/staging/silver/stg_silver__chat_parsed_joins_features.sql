with 

parsed as (
    select * from {{ ref('base_silver__chat_parsed') }}
),

features as (
    select * from {{ ref('base_silver__chat_features') }}
),

join_parsed_and_features as (
    select 
        p.*,
        f.*
    from parsed p
    left join features f
        on p.event_id = f.event_id
)

select * from join_parsed_and_features