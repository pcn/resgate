-- Gauze tables are related to getting meaningful values out of
-- webhook POST data 

create table extractions (
       id INTEGER PRIMARY_KEY,
       hook_id INTEGER NOT NULL UNIQUE,
       jmespath_data TEXT,
       example_message TEXT
       )
