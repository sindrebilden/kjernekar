import os
from slack.Slack import Slack
from threading import Event
from haikubot.bot import Haikubot

class Kjernekar:
    def __init__(self, slack_app_token, slack_bot_token, slack_channel_haiku):
        self.slack = Slack(app_token=slack_app_token, bot_token=slack_bot_token)
        self.haiku = Haikubot()
        self.slack_channel_haiku = slack_channel_haiku

        self.slack.addHandler(self.slack_handler)
        self.slack.connect()
        
        # Deleting ephemeral containers
        self.envelope_id = None


        self.slack.say(self.slack_channel_haiku, 'Hello! :wave:')

    def slack_handler(self, client, req):
        if req.type == "events_api" and req.payload["event"]["type"] == "app_mention" :
            self.slack_mention_handler(req)
        elif req.type == "slash_commands" and req.payload["command"] == '/haiku':
            self.slack_command_haiku_handler(req)   
        elif req.type == "interactive":
            self.slack_handle_interactive(req)   

        print(req.type)

    def slack_mention_handler(self, req):
        self.slack.acknowledge(req)
        self.slack.react(req, emoji='eyes')

    def slack_command_haiku_handler(self, req):
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Haiku"
                    }
                },
                {
                    "type": "section",
                    "block_id": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "What do you want to do?"
                    },
                    "accessory": {
                        "action_id": "action",
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an action"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Create a wordcloud"
                            },
                            "value": "wordcloud"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Create a timeline"
                            },
                            "value": "stats timeline"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Show stats list"
                            },
                            "value": "stats top"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Export haikus"
                            },
                            "value": "export"
                        }
                    ]
                    }
                },
                {
                    "type": "section",
                    "block_id": "section2",
                    "text": {
                    "type": "mrkdwn",
                    "text": "Pick users from the list"
                    },
                    "accessory": {
                    "action_id": "users",
                    "type": "multi_users_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select users"
                    },
                    "max_selected_items": 1 
                    }
                }
            ]
        }
        self.envelope_id = req.envelope_id
        self.slack.acknowledge(req=req, payload=payload)
        
    def slack_handle_interactive(self, req):
        print("HANDLER")
        print(req.payload)
        option = req.payload['state']['values']['section']['action']['selected_option']['value']
        print(option)

        if option == 'wordcloud' or option == 'stats timeline':
            self.slack.acknowledge(
                envelope_id=self.envelope_id, 
                payload={ 
                    "delete_original": "true",
                    "response_type": "ephemeral",
                    "text": 'One {} comming up!'.format(option)
                }
            )
            image, filename = self.haiku.handle_command(option, req.payload["user"]["username"])

            self.slack.upload(
                channel=req.payload['channel']['id'],
                file=image,
                title=filename
            )
        else:      
            self.slack.acknowledge(
                envelope_id=self.envelope_id,
                payload={ 
                    "delete_original": "true",
                    "response_type": "ephemeral",
                                "text": 'I cannot do that'
                }
            )

        # Delete window after command
        """self.slack.delete(
            channel=req.payload['container']['channel_id'],
            ts=req.payload['container']['message_ts']
        )"""
        
    def formatHaiku(self, haiku):
        haiku_id = haiku[0][0]
        haiku_content = haiku[0][1]
        haiku_author = haiku[0][2]

        return {
            "text": haiku_content
        }

if __name__ == "__main__":
    kjernekar = Kjernekar(
        slack_app_token=os.environ.get("SLACK_APP_TOKEN"), 
        slack_bot_token=os.environ.get("SLACK_BOT_TOKEN"),
        slack_channel_haiku='G01622BNT45'
    )



    Event().wait()

    