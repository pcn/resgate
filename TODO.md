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

# Backend

- Save rule


# Frontend


# Test services
Most mocking tests can probably be done for the service by creating an
endpoint that is `/testv1/<true|false>/<until>`. Using the timestamp format of 
`%Y-%m-%d %H:%M:%S` which matches the sqlite default `datetime()` format.
