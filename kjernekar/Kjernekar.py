import os
import json
from slack.Slack import Slack
from threading import Thread, Event

from haiku.Haiku import HaikuHandler

class Kjernekar(Thread):
    def __init__(self):
        self.slack = Slack()
        self.haiku = HaikuHandler(self.slack)
        self.slack.addHandler(self.slack_handler)

        self.slack.connect()

        Event().wait()
        

    def slack_handler(self, client, req):
        if req.type == "events_api" and req.payload["event"]["type"] == "app_mention" :
            self.slack_mention_handler(req)
        elif req.type == "slash_commands" and req.payload["command"] == '/haiku':
            self.haiku.handle_slack_haiku_command(req)   
        elif req.type == "interactive":
            self.haiku.handle_slack_haiku_interactive(req)   

    def slack_mention_handler(self, req):
        self.slack.acknowledge(req)
        self.slack.react(req, emoji='eyes')


if __name__ == "__main__":
    kjernekar = Kjernekar()

