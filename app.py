
import os
import re
from collections import Counter

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

bolt_app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

flask_app = Flask(__name__)
handler = SlackRequestHandler(bolt_app)

CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]

message_count = 0
mention_counts = Counter()

@bolt_app.event("message")
def track_message(event):
    global message_count

    if event.get("channel") != CHANNEL_ID:
        return

    if event.get("subtype") or event.get("bot_id"):
        return

    message_count += 1

    text = event.get("text", "")

    mentioned_users = set(
        re.findall(r"<@([A-Z0-9]+)(?:\|[^>]*)?>", text)
    )

    for user_id in mentioned_users:
        mention_counts[user_id] += 1

    print("Messages:", message_count)
    print("Mentions:", dict(mention_counts))

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@flask_app.route("/", methods=["GET"])
def home():
    return "Slack tracker is running", 200

# Used by Gunicorn when deployed
app = flask_app

