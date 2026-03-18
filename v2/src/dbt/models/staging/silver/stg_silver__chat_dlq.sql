with 

source as (
    select *
    from {{ source('silver','chat_dlq') }}
    
)

select * from source