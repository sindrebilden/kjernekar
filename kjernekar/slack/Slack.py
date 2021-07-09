import os
import json
import urllib3
from threading import Event, Thread
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient

from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest


class Slack(Thread):
    def __init__(self):
        self.client = SocketModeClient(
            app_token=os.environ.get("SLACK_APP_TOKEN"),
            web_client=WebClient(token=os.environ.get("SLACK_BOT_TOKEN")),
        )

    def addHandler(self, handler):
        # Add a new listener to receive messages from Slack
        # You can add more listeners like this
        self.client.socket_mode_request_listeners.append(handler)

    def connect(self):
        self.client.connect()

    def say(self, channel=None, text=None, blocks=None, thread_ts=None, user=None):
        if user is not None:
            self.client.web_client.chat_postEphemeral(
                channel=channel,
                text=text,
                blocks=blocks,
                thread_ts=thread_ts,
                user=user,
            )
        else:
            self.client.web_client.chat_postMessage(
                channel=channel, text=text, blocks=blocks, thread_ts=thread_ts
            )

    def upload(self, channel=None, file=None, title=None):
        self.client.web_client.files_upload(channels=channel, file=file, title=title)

    def respond(self, req, text=None, blocks=None, thread=False, user=None):
        self.say(
            channel=req.payload["event"]["channel"],
            text=text,
            blocks=blocks,
            thread_ts=(req.payload["event"]["ts"] if thread else None),
            user=user,
        )

    def react(self, req, emoji="kj"):
        self.client.web_client.reactions_add(
            name=emoji,
            channel=req.payload["event"]["channel"],
            timestamp=req.payload["event"]["ts"],
        )

    def delete(self, channel, ts):
        self.client.web_client.chat_delete(channel=channel, ts=ts)

    def acknowledge(self, req=None, text=None, payload=None, envelope_id=None):
        eid = envelope_id if req is None else req.envelope_id

        if payload is not None:
            response = SocketModeResponse(
                envelope_id=eid,
                payload=payload,
            )
        elif text is not None:
            response = SocketModeResponse(
                envelope_id=eid,
                payload={"text": text},
            )
        else:
            response = SocketModeResponse(envelope_id=eid)

        self.client.send_socket_mode_response(response)

    def acknowledge_interaction(self, req, text=None):
        url = req.payload["response_url"]

        proxy = os.environ.get("https_proxy")
        if (proxy is None):
            http = urllib3.PoolManager()
        else:
            http = urllib3.ProxyManager(proxy)

        if text is None:
            payload = {"delete_original": "true"}
        else:
            payload = {"text": text, "replace_original": "true"}

        r = http.request(
            "POST",
            url,
            headers={"Content-type": "application/json"},
            body=json.dumps(payload)
        )

    def open_modal(self, trigger_id=None, view=None):
        self.client.web_client.views_open(trigger_id=trigger_id, view=view)

    def update_modal(self, view_id=None, view=None):
        self.client.web_client.views_update(
            view_id=view_id,
            view=view,
        )

    def respond_interaction(self, req, text=None, blocks=None, thread=False):
        self.say(
            channel=req.payload["channel"]["id"],
            text=text,
            blocks=blocks,
            user=req.payload["user"]["id"],
        )

    def load_view(self, filename):
        dirpath = os.path.dirname(__file__)
        filepath = os.path.join(dirpath, filename)
        with open(filepath) as json_file:
            data = json.load(json_file)

            return data


if __name__ == "__main__":
    slack = Slack(
        app_token=os.environ.get("SLACK_APP_TOKEN"),
        bot_token=os.environ.get("SLACK_BOT_TOKEN"),
    )

    slack.connect()

    slack.say(channel="<channel-id>", text="Hello :wave:")
