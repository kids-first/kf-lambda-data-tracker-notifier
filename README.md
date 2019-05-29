Kids First Data Tracker Notifier
================================

A lambda to send notifications for the data tracker.


Configuration
-------------

The lambda needs to be configured with the correct variables in the environment
to be able to send messages to Slack:

- `SLACK_TOKEN` - Token provided by Slack for API use
- `SLACK_CHANNEL` - The channel that notifications will be sent to
- `API_URL` - The url of the Study Creator API
