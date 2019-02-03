import logging
import time

from websocket._exceptions import WebSocketException

from kjernekar import config, VERSION
from kjernekar.connection.slack import Slack
from kjernekar.services.context import Context
from kjernekar.services.responder import Responder

class Kjernekar:
    punish_quarantine = 0

    def __init__(self, api_key):
        self.name = config.BOT_NAME
        logging.info('Running {} v{}'.format(self.name, VERSION))
        self.waitForConnection = 10

        self.slack = Slack(api_key)
        self.responder = Responder(self.slack)

        self.bot_id = self.slack.get_id()
        self._at = '<@{}>'.format(self.bot_id)
        self.connectionInfo = {'died': False, 'channel': None, 'hasConnected': False}

    def run(self):
        try:
            self.join_conversation()
        except WebSocketException:
            logging.error("Could not connect to slack, will retry in {} seconds.".format(self.waitForConnection))
            time.sleep(self.waitForConnection)
            self.run()
        except ValueError:
            raise ValueError
        except Exception as err:
            if config.DEBUG:
                logging.critical("config.DEBUG is set, crashing on failure, error {}".format(err))
                raise Exception

            logging.error('Something unexpected happend, restarting {}. Error: {}'.format(self.name, err))
            self.connectionInfo['died'] = True
            self.run()

    def clean_up(self):
        print("I'm not feeling so well..")

    def join_conversation(self):
        logging.debug("Connecting to slack websocket...")

        if self.slack.connect():
            logging.debug("Connected to slack websocket.")
            self.connectionInfo['hasConnected'] = True

            lastResponse = None
            while True:
                try:
                    response = self.slack.categorize(self.slack.read())
                    self.update_quarantine()
                    if response != None:
                        self.interpret(response, lastResponse)
                        lastResponse = response

                except TimeoutError:
                    logging.error("Timed out while reading from Slack.")
                    continue

                time.sleep(config.READ_WEBSOCKET_DELAY)
        else:
            logging.error("Connection error, unable to connect to Slack.")
            if self.connectionInfo['hasConnected']:
                raise WebSocketException()

            raise ValueError("Unable to connect, bad token or bot ID?")


    def interpret(self, response, lastResponse):


        # A quarantine is set to avoid spam, but is ignored if referenced directly with @BOTNAME
        if self.punish_quarantine == 0 or (response.message != None and self._at in response.message):
            # Trigger with a reaction or message with words in PUNISH.context
            if (Context.PUNISH.incontext(response.message) and response.userid != self.bot_id) \
            or (response.reaction != None and Context.PUNISH.incontext(response.reaction.reaction)):
                message_out = self.responder.create_response(Context.PUNISH, response, lastResponse)

                if response.reaction != None:
                    if self.bot_id in response.reaction.to_user:
                        message_out = self.responder.create_response(Context.DONTPUNISHME, response, lastResponse)
                        self.slack.post_message(message_out, response.channel)
                        return

                elif self._at in response.message or config.BOT_NAME in message_out:
                        message_out = self.responder.create_response(Context.DONTPUNISHME, response, lastResponse)
                        self.slack.post_message(message_out, response.channel)
                        return

                self.slack.post_message(message_out, response.channel)
                self.punish_quarantine = config.PUNISH_QUARANTINE
                return

        # Trigger with a reaction or message with word in SCORE.context
        if (Context.SCORE.incontext(response.message) and response.userid != self.bot_id) \
        or (response.reaction != None and Context.SCORE.incontext(response.reaction.reaction)):
            if response.reaction != None:
                if self.bot_id in response.reaction.to_user:
                    message_out = self.responder.create_response(Context.GRATEFUL, response, lastResponse)
                    self.slack.post_message(message_out, response.channel)
                    return
            elif self._at in response.message:
                    message_out = self.responder.create_response(Context.GRATEFUL, response, lastResponse)
                    self.slack.post_message(message_out, response.channel)
                    return

        # Trigger with @BOTNAME and some greeting defined by the context file GREETING.context
        if Context.GREETING.incontext(response.message) and self._at in response.message:
            message_out = self.responder.create_response(Context.GREETING, response, lastResponse)
            self.slack.post_message(message_out, response.channel)
            return


    def update_quarantine(self):
        if self.punish_quarantine > 0:
            self.punish_quarantine -= 1
