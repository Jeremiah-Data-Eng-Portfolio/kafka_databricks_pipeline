with 

source as (

    select * from {{ source('ops','streaming_batch_metrics')  }}

)

select * from source