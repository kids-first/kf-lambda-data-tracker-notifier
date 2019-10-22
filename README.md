<p align="center">
  <img src="docs/data_tracker_notifier.svg" alt="data tracker notifier logo" width="660px">
</p>
<p align="center">
  <a href="https://github.com/kids-first/kf-lambda-data-tracker-notifier/blob/master/LICENSE"><img src="https://img.shields.io/github/license/kids-first/kf-lambda-data-tracker-notifier.svg?style=for-the-badge"></a>
  <a href="https://kids-first.github.io/kf-api-study-creator/"><img src="https://img.shields.io/readthedocs/pip.svg?style=for-the-badge"></a>
</p>

# Kids First Data Tracker Notifier

A lambda to send notifications for the data tracker.

## Configuration

The lambda needs to be configured with the correct variables in the environment
to be able to send messages to Slack:

- `AUTH0_CLIENT` - Auth0 client id used to authenticate with the study creator
  api
- `AUTH0_SECRET` - Auth0 secret for the client_credentials flow
- `SLACK_TOKEN` - Token provided by Slack for API use
- `SLACK_CHANNEL` - The channel that notifications will be sent to
- `API_URL` - The url of the Study Creator API
- `UI_URL` - The url of the Data Tracker application used to form urls for the
  user to follow
