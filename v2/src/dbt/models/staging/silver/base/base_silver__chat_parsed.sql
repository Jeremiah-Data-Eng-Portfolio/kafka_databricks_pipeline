with 

source as (
    select * from {{ source('silver','silver_chat_parsed') }}
)

select * from source