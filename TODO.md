# How to usefully use a webhook's data 
- Each provider of a webhook will have different shapes for the data
  they send. There will be one set of rules - `inbound_alert_rules`
  that can have a mapping of inbound request fields to fields that
  will be made available in the environment of subsequent parts of the
  process by storing the entire original message for troubleshooting
  and passing in the decoded parts into the appropriate queue
  parts. E.g. with a pagerduty alert that comes from datadog or some
  other service, the important data may be embedded in a message
  within the payload with one shape, but may have different data if it
  comes from e.g. prometheus-alerter. The idea here is that we should
  be able to create one web hook for one kind of pagerduty message, and
  another for a pagerduty message from another source.
  
  See https://developer.pagerduty.com/docs/webhooks/v2-overview/
  
  Datalog? JMESpath (on the maybe safe assumption that everything will be json, or
  json-representable? It's more familiar than datalog)
  
# Backend

- Save rule


# Frontend
