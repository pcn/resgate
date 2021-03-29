# How to usefully use a webhook's data 
- Each provider of a webhook will have different shapes for the data
  they send. There will be one set of rules - `inbound_alert_rules`
  that can have a mapping of inbound request fields to fields that
  will be made available in the environment of subsequent parts of the
  process by storing the entire original message for troubleshooting
  and passing in the decoded parts into the appropriate queue
  parts. E.g. with a pagerduty alert that comes from datadog or somew
  other service, the important data may be embedded in a message
  within the payload with one shape, but may have different data if it
  comes from e.g. prometheus-alerter. The idea here is that we should
  be able to create one web hook for one kind of pagerduty message, and
  another for a pagerduty message from another source.
  
  See https://developer.pagerduty.com/docs/webhooks/v2-overview/
  
  JMESpath (on the maybe safe assumption that everything will be json, or
  json-representable? It's more familiar than datalog)

# Tags

Every service will have a set of tags, which will be a key:value
mapping of <string>:<string>. Some of the tags can be pulled from
webhook-provided data, and some tags will be defined as overridable
defaults. These should be separate.

# Rules

Rules get stored in rules groups. Here's how I think they'll work

1. Each rule is a line that gets stored in a TEXT field in the database. The rules need
to be separated line by line.
1. Each rule must have a name. That name will be stored in the DB, looked up applied etc.
1. Each rule group should probably be run independently of each other. Note: not sure if 
   this is likely to cause issues? Still need to see what this looks like.
1. Some rules are special, and their names are reserved, and there can only be one of each per rule_group:
  a. rule\_name - mandatory - this will also become the name of the rule group in the db
  a. fixer\_endpoint: requred - any rules like this will have as the first fact a url 
     that will be checked with other facts passed in as pairs of  "key", "value" arguments, which
     will be sent to the checking endpoint as a single-depth json object as part of a POST request.
     Note that this endpoint must return a json document that can be passed to the check\_running\_endpoint 
  a. fixer\_running\_endpoint -  required - 
     Anyway, this goes to a function that will check whether the test is still running.
  a. check\_resolved\_endpoint - optional - similar structure to the above, the first fact must be a url etc. etc.
     This url will check whether the issue has resolved afer a fixer has been invoked. 
     The keys should be regular strings, but the values can refer to facts or tags when checked,
     which should bring in tags extracted from the alert, for e.g.? How can 
     I do this? 
  a. required\_tags - optional - if any tags are going to be used, this is required so that these 
     tags can be pulled in from the alert and checked to see if those tags have been extracted
     from the message.j

How do I get the tags from the alert into the rules processing?

# Backend

- Save rule


# Frontend


# Test services
~~ Most mocking tests can probably be done for the service by creating an
endpoint that is `/testv1/<true|false>/<until>`. Using the timestamp format of 
`%Y-%m-%d_%H:%M:%S` which almost the sqlite default `datetime()` format (except
for the `_` which makes using this from the command line much simpler) ~~


## Using the above endpoints, construct tests

Use the test endpoints to construct tests that can succeed, fail
