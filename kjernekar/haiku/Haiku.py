import os
import logging
from haikubot.bot import Haikubot
from repo.repo import RepoWatcher

class HaikuHandler():
    def __init__(self, slack):
        self.slack = slack
        self.haikubot = Haikubot()
        self.repo = RepoWatcher(
            repo_url=os.environ.get("REPOSITORY_URL"),
            basic_auth=os.environ.get("REPOSITORY_BASIC_AUTH"),
            poll_interval=int(os.environ.get("REPOSITORY_POLL_INTERVAL", 30)),
            callback=self.handle_response
        )
        self.slack_channel_haiku = os.environ.get("SLACK_HAIKU_CHANNEL")

        self.repo.start()


    def handle_response(self, pull_requests=[]):
        for pull_request in pull_requests:
            parsed = self.parse_haiku(pull_request)

            if not parsed:
                continue

            haiku, author, link = parsed
            self.store_haiku(haiku, author, link)

    
    def parse_haiku(self, pull_request=None):
        if pull_request is None:
            return False

        if not isinstance(pull_request, dict) or 'description' not in pull_request:
            logging.debug('Pull-request has no description')
            return False

        haiku=pull_request['description']
        author=pull_request['author']['user']['displayName']
        link=pull_request['links']['self'][0]['href']

        return haiku, author, link        

    def store_haiku(self, haiku=None, author=None, link=None):
        haiku_id = self.haikubot.store_haiku(haiku, author, link)

        if haiku_id:
            logging.debug('Posting haiku #{} to {}'.format(haiku_id, self.slack_channel_haiku))

            posted = self.post_haiku(haiku_id, haiku, author, link)

            if posted:
                self.haikubot.mark_posted(haiku_id)

            return True

        return False

    def post_haiku(self, haiku_id=None, haiku=None, author=None, link=None):
        if haiku is None:
            logging.debug('Haiku #{} has no content'.format(haiku_id))
            return False


        self.slack.say(
            channel=self.slack_channel_haiku,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*<{}|Haiku #{}>*".format(link, haiku_id)
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ">{}".format(haiku.replace('\n', '\n>'))
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "- {}".format(author)
                        }
                    ]
                }
            ]
        )
        return True

    def handle_slack_haiku_command(self, req):
        option=req.payload['text']
        
        if 'help' in option:
            success = False
        else:
            success = self._haiku_handle_command(
                option=option, 
                user=req.payload["user_name"],
                channel=req.payload['channel_id'],
                req=req,
                acknowledge_callback=self.slack.acknowledge
            )

        if not success:
            payload = self.slack.load_view('interactive.json')
            self.slack.acknowledge(req=req, payload=payload)
        
    def handle_slack_haiku_interactive(self, req):
        print(req.payload)

        if req.payload['type'] == 'block_actions':
            option = req.payload['state']['values']['section']['action']['selected_option']['value']
            if 'create_new' == option:
                trigger_id=req.payload['trigger_id']
                view=self.slack.load_view('new_haiku_modal.json')

                self.slack.open_modal(trigger_id, view)

                self.slack.acknowledge_interaction(req)
                return

            else:
                self._haiku_handle_command(
                    option=option, 
                    user=req.payload["user"]["username"],
                    channel=req.payload['channel']['id'],
                    req=req,
                    acknowledge_callback=self.slack.acknowledge_interaction
                )
                return
        
        if req.payload['type'] == 'view_submission' and req.payload['view']['callback_id'] == 'new-haiku-modal':
            self._create_new_haiku(req)
            self.slack.acknowledge(req, payload={ "response_action": "clear" })

    def _create_new_haiku(self, req):
        logging.debug('Creating new haiku')

        user=req.payload["user"]["username"]
        link=req.payload["view"]["state"]["values"]["link-block"]["link-input"]["value"]
        haiku=req.payload["view"]["state"]["values"]["haiku-block"]["haiku-input"]["value"]

        self.store_haiku(haiku, user, link)


    def _haiku_handle_command(self, option, user=None, channel=None, req=None, acknowledge_callback=None):
        if 'wordcloud' in option or 'stats timeline' in option:
            acknowledge_callback(req)

            result =self.haikubot.handle_command(option, user)

            if result == False:
                acknowledge_callback(req, text="Couldn't create {}".format(option))
                return False
                
            acknowledge_callback(req)
            image, filename = result
            self.slack.upload(channel=channel,file=image,title=filename)
            return True
        elif 'stats top' in option:
            stats = self.haikubot.handle_command(option, user)

            if len(stats) < 1:
                acknowledge_callback(req, text="Couldn't find any haikus.")
                return False
            else:
                acknowledge_callback(req)
                
                self.slack.say(channel=channel, blocks=self.format_stats(stats))
            return True
        elif 'show' in option:
            result = self.haikubot.handle_command(option, user)

            if result[0] == False:
                success, message = result
                acknowledge_callback(req, text=message)

                return False
            acknowledge_callback(req)

            self.post_haiku(haiku.hid, haiku.haiku, haiku.author, haiku.link)
            return True
        else:      
            return False


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