# resgate
Observe your infrastructure rescue itself.

# Why

First, why the name? Is it "res" and "gate"? No, it's the portuguese
word for "rescue". Res-gatch-eeee for us americans.

The idea with resgate is that it fills in a very small, but important
niche in closing the monitoring-alerting-resolution loop that tells us
both that there's a problem, and that we've fixed it.

Ideally, when we create a software infrastructure using devops and SRE
principles, we record metrics about it - see the "Golden Signals" for
e.g.  which are essentially:

- Latency
- Traffic
- Errors
- Saturation

Also for individual host investiation, see Brendan Gregg's descrption
of his USE method, which measures utilization, saturation, and
errors. Look similar?

So once monitoring has been set up, and you have metrics, an alerting
system will be the next step in managing your infrastructure. Once
that is created, you will begin to appreciate how much work you can
create for yourself, and probable find that you need to start turning 
problems that you are familiar with into solutions.

The first steps is that as you begin to understand your
infrastructure, you will create runbooks, describing the alert you've
created, and what to do to remedy that alert. Run this command, endit
this script, reboot this node, re-install the OS, etc. Very often, it
looks something like this:

![can't a machine do this?](https://media.giphy.com/media/DUtVdGeIU8lmo/giphy.gif)

In a distributed environment, some things should become clear really fast:
1. This isn't an important business competency. Restarting our service isn't part of what makes our service better than a competitor. 
2. This works when things are small, but in a larger environment, we don't just have one process, or one container, or one pod, or one deployment. We have complex interacting pieces that have certain rules.

However

3. The fundamental pieces of this are completely automatable.

Using tools that provide you with distributed ssh, you are effectively
able to do certain actions all at once, or in batches but you end up having
to solve the subtle problems:

1. You can restart all of service X, *unless* there is a deployment happening.
2. You can run a deployment, *unless* there is an existing deployment running.
3. You can scale down because you have extra resources *unless* there is a large queue of inbound requests that aren't being handled yet (prevent yo-yoing, which would cause a delay)

etc. In general, each of these situations seem very specific to your
organization, and your ops/devops/sre team will spend some time
working on creating some rules for this work for a specific service,
because the first few times you do this, the different services behave
differently.

Once this is done, you may find you're done! This is your scale
forever. But once you get to your first plateau, you get the next
problem: with more services, or microservices, you need to look at the
status of multiple services.

# The other hidden problem

The other problem being addressed here is that alerts happen at a
point in time based on the conditions they are given. E.g. "log
message says X", "metric Y has gone above a threshhold for 10
minutes".

The resolutions seem similar: At a certain point, the log message
hasn't been seen, and the metric goes below the threshold. 

However, that is a process, and resolution is not an instant
point-in-time event from start to finish. A service is deployed and
the problem isn't resolved because of the deployment!  It's resolved
when the new deployment has completed and the conditions have been
met! And if the deployment takes 10 minutes, but the alert fires every
5 minutes, you don't want to start a new deployment before the old one
has had time to warm up and come into full service. Let's call this
the "robo-hammer" problem. The simple solution will end up
perpetuating the problem. Even a blue-green deploy will not
automatically fix this because some deployment strategies could,
potentially, result in the new deployment being thrown out, and the
old alerting service continuing to run as an even newer generation is
deployed again and again by the robo-hammer.

# The proposed solution

I think that a generally useful process to help this can be created. The important things are that:

1. Your alerting service feeds alerts to a webhook with a schema'd json message that resgate knows how to 
   read, some of which will be passed to the remediation event.
2. Every alert it knows about is tagged with a label that can be used with simple boolean logic.
3. The logic of whether you can fire a remediation will be done with a logic language, so it can be stored,
   run, modeled, tested, without needing an alert.
4. Every alert that is received and could be remediated will be checked against tags, using logic you define, to 
   determine if it is actionable, or if it needs to be deferred, discarded, or collapsed into another occuring event.
5. Ever remediation event that is initiated will have an event ID that is returned from the "remediator" that can be
   used to identify it.
6. Every remediation event will also have an endpoint that can be provided with the remediation event ID as an 
   argument, which is capable of checking whether the task associated with the ID has completed.

# Testing:
In a virtualenv:
```
$ pip install -e .
$ resgate-server

```

## Running

Wherever you run this from needs the following directories:

- 'plaster': DB of JMESpath for destructuring inbound alert webhooks, and 
  rules (an old name for a band-aid. healing. Right.)
- 'logs': program logs and event data will be put here
- 'queues': as events come in, they'll be queued here, consumed and then removed.


Run the main migration:
```
 $ mkdir -p plaster
 $ sqlite3 plaster/data.db '.read migrations/01-plaster.sql
```

Add some test data (from a sqlite3 CLI)
```
insert into rule_groups (name) values ("this is my first test")
insert into rule_groups (name) values ("this is my second test")
```

And start it up:
```
PYTHONPATH=lib bin/run_webserver.py 
```

And add this rule from the "edit_rules" choice from [here]('http://localhost:8080/tool'):
```
# Write some datalog to name this
rule_name(1 "This is my first test")
rule_check_url("https:/localhost:8080/always_true")
```
