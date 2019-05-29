import os
import json
import re
import boto3
from base64 import b64decode
from botocore.vendored import requests


def handler(event, context):
    """
    Send a release event to slack
    """
    if "Records" not in event or len(event["Records"]) < 1:
        return

    if "Sns" not in event["Records"][0]:
        return

    api_url = os.environ.get("API_URL", "")

    ev = json.loads(event["Records"][0]["Sns"]["Message"])

    attachments = []
    slack_msg = {
        "username": "Data Tracker Bot",
        "icon_emoji": ":man_health_worker:",
    }
    message = f"Your Message Here!"

    attachment = {"fallback": ev["message"], "text": message}

    button = {
        "fallback": f"Your message here",
        "text": f"Your message here",
        "actions": [
            {"type": "button", "text": "View Now", "url": "http://example.com"}
        ],
    }
    attachments.append(button)

    slack_msg["attachments"] = attachments

    if "SLACK_TOKEN" in os.environ and "SLACK_CHANNEL" in os.environ:
        kms = boto3.client("kms", region_name="us-east-1")
        SLACK_SECRET = os.environ.get("SLACK_TOKEN", None)
        SLACK_TOKEN = (
            kms.decrypt(CiphertextBlob=b64decode(SLACK_SECRET))
            .get("Plaintext", None)
            .decode("utf-8")
        )
        SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "").split(",")
        SLACK_CHANNEL = [
            c.replace("#", "").replace("@", "") for c in SLACK_CHANNEL
        ]

        for channel in SLACK_CHANNEL:
            slack_msg["channel"] = channel

            resp = requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": "Bearer " + SLACK_TOKEN},
                json=slack_msg,
            )
