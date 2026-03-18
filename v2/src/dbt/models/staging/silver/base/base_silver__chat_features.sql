with 

source as (

    select * from {{ source('silver','silver_chat_features')  }}

)

select * from source 