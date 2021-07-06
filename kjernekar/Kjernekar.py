import os
import json
from slack.Slack import Slack
from utils.color import string_to_color_hex
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
        payload = self.slack.load_view('interactive.json')
        self.slack.acknowledge(req=req, payload=payload)
        
    def slack_handle_interactive(self, req):
        option = req.payload['state']['values']['section']['action']['selected_option']['value']
        
        if option == 'wordcloud' or option == 'stats timeline':
            self.slack.acknowledge_interaction(req)

            image, filename = self.haiku.handle_command(option, req.payload["user"]["username"])
            self.slack.say(
                channel=req.payload['channel']['id'],
                text="A {} comming up!"
            )
            self.slack.upload(
                channel=req.payload['channel']['id'],
                file=image,
                title=filename
            )
        elif option == 'stats top':
            stats = self.haiku.handle_command(option, req.payload["user"]["username"])

            if len(stats) < 1:
                self.slack.acknowledge_interaction(req, text="Couldn't find any haikus.")
                return
            else:
                self.slack.acknowledge_interaction(req)
                
                self.slack.say(
                    channel=req.payload['channel']['id'],
                    blocks=self.format_stats(stats)
                )
        else:      
            self.slack.acknowledge_interaction(req, text='I cannot do that!')


    def format_stats(self, stats):
        title = 'Haiku stats: # of haikus per user'
        attachments = [{
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": title
            }
        }]
        
        for i in range(len(stats)):
            attachments.append({
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": self.format_placement(i + 1)
				}, #TODO: Legg inn generert bilde med farge
				{
					"type": "mrkdwn",
					"text": "With {} haiku: @{}".format(stats[i][1], stats[i][0])
				}
			]
		})

        return attachments

    def format_placement(self, place):
        if (place == 1):
            return ':first_place_medal:'
        if (place == 2):
            return ':second_place_medal:'
        if (place == 3):
            return ':third_place_medal:'
        
        return '#{}'.format(place)

        
    def format_haiku(self, haiku):
        haiku_id = haiku[0][0]
        haiku_content = haiku[0][1]
        haiku_author = haiku[0][2]
        haiku_link = haiku[0][4]

        return {
            'type': 'mrkdwn',
            'text': "<{}|Haiku #{}> \n{}".format(haiku_link, haiku_id, haiku_content),
            'color': string_to_color_hex(stats[i][0])
        }

if __name__ == "__main__":
    kjernekar = Kjernekar(
        slack_app_token=os.environ.get("SLACK_APP_TOKEN"), 
        slack_bot_token=os.environ.get("SLACK_BOT_TOKEN"),
        slack_channel_haiku='G01622BNT45'
    )

    Event().wait()
