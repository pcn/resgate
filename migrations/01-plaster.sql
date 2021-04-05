-- Tables to do with rules and rule groups and define webhooks
create table webhooks (
       id INTEGER primary key,
       name TEXT NOT NULL UNIQUE,
       path TEXT NOT NULL UNIQUE,   -- The inbound path
       queue_name TEXT NOT NULL
       );

-- create table rule_map ( -- map a webhook to its entry point rule
--        id INTEGER primary key,
--        webhook_id INTEGER,
--        rule_id INTEGER,
--        UNIQUE(webhook_id, rule_group_id)
--        );

create table rules (
       id INTEGER primary key,
       name TEXT NOT NULL UNIQUE,
       rule TEXT NOT NULL,
       );
  
