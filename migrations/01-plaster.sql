-- Tables to do with rules and rule groups and define webhooks
create table webhooks (
       id INTEGER primary key,
       name TEXT NOT NULL UNIQUE,
       path TEXT NOT NULL UNIQUE,   -- The inbound path
       queue_name TEXT NOT NULL
       );

create table rule_groups (
       id INTEGER primary key,
       name TEXT NOT NULL UNIQUE -- Name of the group
       );


create table rule_group_map ( -- map rule groups to webhooks
       id INTEGER primary key,
       webhook_id INTEGER,
       rule_group_id INTEGER,
       UNIQUE(webhook_id, rule_group_id)
       );

create table rules  (
       id INTEGER primary key,
       rule_group INTEGER NOT NULL,  -- A group of rules that will be read together
       rule TEXT NOT NULL,
       UNIQUE(rule_group, rule)
       );
  
  
