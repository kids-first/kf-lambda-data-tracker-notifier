def summary_header(url, date):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Here's what happened yesterday, {date.strftime('%Y/%m/%d')}, in the Data Tracker*",
        },
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",
                "emoji": True,
                "text": "Update your Notifications :loud_sound:",
            },
            "url": url,
        },
    }


def study_header(url, study_id, study_name):
    message = f":file_cabinet: `{study_id}` *{study_name}*\nHere is a summary of recently active files in this study"
    return {
        "type": "section",
        "text": {"type": "mrkdwn", "text": message},
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",
                "emoji": True,
                "text": "View Study :file_cabinet:",
            },
            "url": url,
        },
    }


def document_header(url, kf_id, title, deleted=False):
    if not deleted:
        message = f":file_folder: `{kf_id}` *{title}*"
    else:
        message = ":no_entry: *File was deleted*"

    message += "\nBelow are recent events to this file."

    message = {"type": "section", "text": {"type": "mrkdwn", "text": message}}
    if not deleted:
        message["accessory"] = {
            "type": "button",
            "text": {
                "type": "plain_text",
                "emoji": True,
                "text": "View Document :mag:",
            },
            "style": "primary",
            "url": url,
        }
    return message


def event(author, author_picture, time, message):
    return {
        "type": "context",
        "elements": [
            {"type": "image", "image_url": author_picture, "alt_text": author},
            {"type": "mrkdwn", "text": f"*{author}* {time}: _{message}_"},
        ],
    }
