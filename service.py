import os
import json
import boto3
import datetime
import time
import re
import logging
from base64 import b64decode
from botocore.vendored import requests
from collections import defaultdict

from queries import ALL_EVENTS, ALL_USERS
from components import summary_header, study_header, document_header, event

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class APIClient:
    def __init__(self, api_url, headers):
        self.api = api_url
        self.session = requests.session()
        self.session.headers.update(headers)

        # Cache events fetched for particular studies
        self.study_cache = {}

    def get_users(self):
        resp = self.session.post(
            self.api, json={"query": ALL_USERS}, timeout=10
        )
        return resp.json()["data"]["allUsers"]["edges"]

    def get_study_events(self, study_id):
        """
        Get all events for a single study on a given date
        """
        if study_id in self.study_cache:
            return self.study_cache

        # start of today
        # today = datetime.datetime.combine(datetime.datetime.today().date(), datetime.time(0, 0, 0))
        today = datetime.datetime.now()
        # start of yesterday
        yesterday = today - datetime.timedelta(days=1)

        variables = {
            "studyId": study_id,
            "createdAt_Lt": today.isoformat(),
            "createdAt_Gt": yesterday.isoformat(),
            "orderBy": "-created_at",
        }

        resp = self.session.post(
            self.api + "/graphql",
            json={"query": ALL_EVENTS, "variables": variables},
            timeout=10,
        )

        events = resp.json()["data"]["allEvents"]["edges"]
        self.study_cache[study_id] = events
        return events


def get_access_token():
    """
    Retrieve an access token from Auth0 so that we may use the study creator
    api
    """
    client_id = os.environ.get("AUTH0_CLIENT")
    client_secret = os.environ.get("AUTH0_SECRET")
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": "https://kf-study-creator.kidsfirstdrc.org",
        "grant_type": "client_credentials",
    }

    resp = requests.post(
        "https://kids-first.auth0.com/oauth/token", json=payload
    )
    if resp.status_code != 200 or "access_token" not in resp.json():
        logger.info("Could not get an access token from Auth0")
        return

    return resp.json()["access_token"]


class UserNotifier:
    def __init__(self, api, url):
        # API Client
        self.api = api
        # Url for the UI
        self.url = url
        self.date = datetime.datetime.today() - datetime.timedelta(days=1)

        # Set up slack creds
        if "SLACK_TOKEN" in os.environ:
            kms = boto3.client("kms", region_name="us-east-1")
            SLACK_SECRET = os.environ.get("SLACK_TOKEN", None)
            SLACK_TOKEN = (
                kms.decrypt(CiphertextBlob=b64decode(SLACK_SECRET))
                .get("Plaintext", None)
                .decode("utf-8")
            )

        headers = {"Authorization": "Bearer " + SLACK_TOKEN}
        self.session = requests.session()
        self.session.headers.update(headers)

        # Cache for formatted messages by study
        self.study_messages = {}

    def format_url(self, url):
        """ Adds additional utm code to a url """
        return f"{url}?utm_source=slack_daily_dm"

    def send_message(self, user, blocks):
        message = {
            "channel": user["slackMemberId"],
            "blocks": blocks,
            "username": "Data Tracker Bot",
            "icon_emoji": ":file_cabinet:",
        }

        resp = self.session.post(
            "https://slack.com/api/chat.postMessage", json=message
        )

    def make_study_message(self, study):
        """
        Make an event timeline for a study
        """
        if study["kfId"] in self.study_messages:
            return self.study_messages[study["kfId"]]

        logger.info(f"Building message for study {study['kfId']}")

        study_id = study["kfId"]
        study_name = study["name"]

        blocks = []
        # Header
        blocks.append(
            study_header(
                self.format_url(f"{self.url}/studies/{study_id}"),
                study_id,
                study_name,
            )
        )

        study_events = self.api.get_study_events(study_id)

        file_timelines = defaultdict(list)
        file_names = {}

        for i, ev in enumerate(reversed(study_events)):
            if ev["node"] is None:
                continue

            # Fil was deleted
            if (
                ev["node"]["eventType"] == "SF_DEL"
                or ev["node"]["file"] is None
            ):
                file_id = re.match(
                    r".*(SF_[A-Z0-9]{8}).*", ev["node"]["description"]
                ).group(1)
            else:
                file_id = ev["node"]["file"]["kfId"]
                file_names[file_id] = ev["node"]["file"]["name"]

            user = ev["node"].get("user")
            if user:
                author = ev["node"]["user"].get("username", "Anonymous user")
                picture = ev["node"]["user"].get(
                    "picture",
                    "https://api.slack.com/img/blocks/bkb_template_images/profile_3.png",
                )
            else:
                author = "Anonymous user"
                picture = "https://api.slack.com/img/blocks/bkb_template_images/profile_3.png"
            dt = datetime.datetime.strptime(
                ev["node"]["createdAt"], "%Y-%m-%dT%H:%M:%S.%f+00:00"
            )
            message = ev["node"]["description"]

            event_message = event(
                author, picture, dt.strftime("%I:%M %p"), message
            )
            file_timelines[file_id].append(event_message)

        deleted = []

        for file_id, timeline in file_timelines.items():
            file_name = file_names.get(file_id)
            # Prepend the deleted files to the beginning of the study's events
            if file_name is None:
                header = document_header(
                    self.url, file_id, "File was deleted", deleted=True
                )
                deleted.append(header)
            else:
                header = document_header(
                    self.format_url(
                        f"{self.url}/studies/{study_id}/documents/{file_id}"
                    ),
                    file_id,
                    file_name,
                )
                blocks.append(header)
                blocks.extend(timeline)

        # Prepend deleted files
        for timeline in deleted:
            blocks.insert(1, timeline)

        self.study_messages[study["kfId"]] = blocks
        return blocks

    def daily_notifications(self):
        """
        Send notifications to users
        """
        users = self.api.get_users()
        logger.info(f"Found {len(users)} potential users to notify")
        # Iterate through users
        for user in users:
            if (
                user["node"]["slackNotify"]
                and user["node"]["slackMemberId"]
                and len(user["node"]["studySubscriptions"]["edges"]) > 0
            ):
                logger.info(f"Notifying {user['node']['username']}")
                self.notify_user(user["node"])

    def notify_user(self, user):
        """
        Send a user notifications for their interested studies
        """
        summary = summary_header(self.format_url(self.url), self.date)
        blocks = [summary]

        for study in user["studySubscriptions"]["edges"]:
            messages = self.make_study_message(study["node"])
            if len(messages) > 1:
                blocks.extend(messages)

        self.send_message(user, blocks)


def handler(event, context):
    """
    """
    start = time.time()
    api_url = os.environ.get("API_URL", "http://study-creator.kids-first.io")
    ui_url = os.environ.get(
        "UI_URL", "https://kf-ui-data-tracker.kidsfirstdrc.org"
    )

    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    api = APIClient(api_url, headers)
    notifier = UserNotifier(api=api, url=ui_url)

    notifier.daily_notifications()
    logger.info(f"Took {time.time() - start}s to run notifications")
