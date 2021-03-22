from pytest_bdd import scenario, given, when, then

@scenario('webhook_listener.feature', 'The webhook listener service is running')
def test_webhook_listener_is_listening():
    pass
