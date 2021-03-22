Feature: Listener for webhooks
  A webhook is listening for incoming requests

  Scenario: The webhook listener service is running
    Given: The service has been started
    When: I connect to the webhook port 9876
    And: I send a test message
    Then: I receive a 200 response
