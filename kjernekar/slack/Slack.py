import os
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient

from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest

class Slack:
    def __init__(self, app_token=None, bot_token=None):
        # Initialize SocketModeClient with an app-level token + WebClient
        self.client = SocketModeClient(
            app_token=app_token,
            web_client=WebClient(token=bot_token)
        )

    def addHandler(self, handler):
        # Add a new listener to receive messages from Slack
        # You can add more listeners like this
        self.client.socket_mode_request_listeners.append(handler)

    def connect(self):
        self.client.connect()

    def say(self, channel=None, text=None, blocks=None, thread_ts=None):
        self.client.web_client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=blocks,
            thread_ts=thread_ts    
        )

    def respond(self, req, text=None, blocks=None, thread=False):
        self.say(
            channel=req.payload["event"]["channel"],
            text=text,
            blocks=blocks,
            thread_ts=(req.payload["event"]["ts"] if thread else None)
        )
    
    def react(self, req, emoji='kj'):

        print(req.payload["event"]["channel"], req.payload["event"]["ts"])
        self.client.web_client.reactions_add(
            name=emoji,
            channel=req.payload["event"]["channel"],
            timestamp=req.payload["event"]["ts"],
        )

    def acknowledge(self, req, payload=None):
        response = SocketModeResponse(envelope_id=req.envelope_id, payload=payload)
        self.client.send_socket_mode_response(response)


if __name__ == "__main__":
    slack = Slack(
        app_token=os.environ.get("SLACK_APP_TOKEN"), 
        bot_token=os.environ.get("SLACK_BOT_TOKEN")
    )

    def process(client: SocketModeClient, req: SocketModeRequest):
        print(req.type)
        print(req.payload)
        if req.type == "events_api" and req.payload["event"]["type"] == "app_mention" :
            # Acknowledge the request anyway
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)
            
            slack.respond(req, text='Hei hei!')
            
            slack.react(req, emoji='eyes')

        # Handle haiku
        if req.type == "slash_commands" and req.payload["command"] == "/haiku":           
            #TODO: Check which action or post buttons?
            response = SocketModeResponse(
                envelope_id=req.envelope_id, 
                payload={
                    "text": 'test'
                }
            )
            client.send_socket_mode_response(response)

            slack.say(channel=req.payload["channel_id"], text=req.payload["text"])
        


    slack.addHandler(process)

    slack.connect()

    slack.say(channel='G01622BNT45', text='Hello :wave:')

    Event().wait()