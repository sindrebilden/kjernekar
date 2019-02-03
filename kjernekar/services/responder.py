import logging
import random
import re
from enum import Enum, auto

from pkg_resources import resource_string, resource_listdir

from kjernekar import config

class Responder:

    TARGET = '{target}'
    SENDER = '{sender}'
    BOTNAME = '{botname}'

    def __init__(self, slackclient):
        self.slack = slackclient

    def load_responses(self, context):
        responsefile = resource_string('kjernekar.services.responsefiles', '{}.response'.format(context.name)).decode('utf-8')
        return list(filter(None, [response.strip() for response in responsefile.split('\n')]))

    def create_response(self, context, slackmessage, lastSlackmessage):
        response = random.choice(self.load_responses(context))

        if self.BOTNAME in response:
            response = response.replace(self.BOTNAME, config.BOT_NAME.capitalize())

        if self.SENDER in response:
            username = self.slack.get_user_name(slackmessage.userid)
            response = response.replace(self.SENDER, username)

        if self.TARGET in response:
            username = self.slack.get_user_name(self.extract_target(slackmessage, lastSlackmessage))
            response = response.replace(self.TARGET, username)

        return response

    def extract_target(self, slackmessage, lastSlackmessage):
        if slackmessage.action == 'reaction_added':
            return slackmessage.reaction.to_user
        elif slackmessage.action == 'message':
            target = re.search("<@(.*)>", slackmessage.message)
            if target != None:
                return target.groups()[0]
            else:
                return lastSlackmessage.userid
        else:
            return lastSlackmessage.userid
