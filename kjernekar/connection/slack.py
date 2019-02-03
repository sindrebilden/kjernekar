import logging
from enum import Enum
from datetime import datetime
import pprint

pp = pprint.PrettyPrinter(indent=4)


from slackclient import SlackClient

from kjernekar import config

class SlackResponse:
    def __init__(self, userid, user_action):
        self.userid = userid
        self.action = user_action

        self.channel = None
        self.response_id = None
        self.message = None
        self.reaction = None
        self.file_id = None

    def __str__(self):
        response = "Slack Response {} \n".format(self.response_id)
        response += "User {} ".format(self.user, self.action)
        if self.message != None:
            response += "wrote {}.".format(self.message)
        if self.reaction != None:
            response += "reacted with :{}: to {}'s post.".format(self.reaction.reaction, self.reaction.to_user)
        if self.file_id != None:
            response += "uploaded file with id:{}.".format(self.file_id)

        return response

class Reaction:
    def __init__(self, reaction, to_user):
        self.reaction = reaction
        self.to_user = to_user

class Slack:
    def __init__(self, api_key):
        if api_key is None:
            raise ValueError('API token for slack is required.')

        self.client = SlackClient(api_key)

    def connect(self):
        return self.client.rtm_connect()

    def read(self):
        return self.client.rtm_read()

    def get_users(self):
        logging.debug("Getting users")

        api_call = self.client.api_call('users.list')

        if api_call.get('ok'):
            users = {}
            for member in api_call.get('members'):
                users[member['id']] = {
                    'name': member['name'],
                    'bot': member['is_bot']
                    }
        return users

    def get_id(self):
        logging.debug('Getting bot id')
        users = self.get_users()
        for userid, user in users.items():
            if user['name'] == config.BOT_NAME and user['bot'] == True:
                return userid
        return None

    def get_user_name(self, userid):
        user = self.client.server.users.find(userid)
        if user == None:
            return None
            
        try:
            return user.real_name.split(" ")[0]
        except:
            return user.name

    def get_channel_name(self, channelid):
        return self.client.server.channels.find(channelid)

    def get_channel_info(self, channelid):
        return self.client.api_call('channels.info', channel=channelid)

    def post_message(self, message, channel=config.POST_TO_CHANNEL, as_user=True):
        if config.DEBUG:
            channel = config.POST_TO_CHANNEL

        if isinstance(message, list):
            return self.client.api_call('chat.postMessage', channel=channel, as_user=as_user, attachments=message)
        return self.client.api_call('chat.postMessage', channel=channel, as_user=as_user, text=message)


    def categorize(self, response):
        if len(response) > 0:
            for external in response:
                if external and external['type'] not in ['hello', 'desktop_notification', 'user_typing', 'reaction_removed']:
                    try:
                        internal = SlackResponse(external['user'], external['type'])

                        if external['type'] != 'user_typing':
                            internal.response_id = external['ts']

                        if external['type'] == 'message':
                            internal.message = external['text']

                        if external['type'] == 'reaction_added':
                            internal.channel = external['item']['channel']
                            internal.reaction = Reaction(external['reaction'], external['item_user'])
                        elif external['type'] == 'reaction_removed':
                            internal.channel = external['item']['channel']
                            internal.reaction = Reaction(external['reaction'], external['item_user'])
                        else:
                            internal.channel = external['channel']

                        if external['type'] == 'file_shared':
                            internal.file_id = external['file_id']

                        return internal
                    except:
                        print("Uhm.. nå er det noe jeg ikke forstår")
                        pp.pprint(external)
                        continue
        return
