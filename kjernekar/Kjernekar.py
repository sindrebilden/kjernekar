import os
from slack.Slack import Slack
from threading import Event

class Kjernekar:
    def __init__(self, slack_app_token, slack_bot_token):
        self.slack = Slack(  app_token=slack_app_token, bot_token=slack_bot_token)
        self.haiku = 

        self.slack.addHandler(self.slack_handler)
        self.slack.connect()

    def slack_handler(self, client, req):
        if req.type == "events_api" and req.payload["event"]["type"] == "app_mention" :
            self.slack_mention_handler(req)
        if req.type == "slash_commands" and req.payload["command"] == '/haiku':
            self.slack_command_haiku_handler(req)   

    def slack_mention_handler(self, req):
        self.slack.acknowledge(req)
        self.slack.react(req, emoji='eyes')

    def slack_command_haiku_handler(self, req):
        payload = {
            "text": 'test'
        }
        self.slack.acknowledge(req, payload)
        

if __name__ == "__main__":
    kjernekar = Kjernekar(
        slack_app_token=os.environ.get("SLACK_APP_TOKEN"), 
        slack_bot_token=os.environ.get("SLACK_BOT_TOKEN"),

    )

    Event().wait()