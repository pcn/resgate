insert into webhooks (id, name, path, queue_name, entry_rule_name) values (100, "foo", "foo", "foo", "foo_entry_rule");

insert into extractions (id, name, hook_id, jmespath_data, example_message) values (100, "foo_extraction", 100,
  "{ service_name: messages[0].incident.service.name, incident_id: messages[0].incident.id }", "");

insert into rules(id, name, rule) values (100, "foo_entry_rule", "rule_name('This is a rule name')");
