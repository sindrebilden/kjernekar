import logging
import os

# Slack
SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')
BOT_NAME= 'kjernekar'
POST_TO_CHANNEL = 'kjernekar-test'
SUPER_MOD = 'Sindre'
READ_WEBSOCKET_DELAY = 1 # seconds

# Debug
DEBUG = True
DEBUG_URL = 'data/debug.json'

# Context spesific
PUNISH_QUARANTINE = 30 # reads, to avoid spam

# logging
LOG_PATH = '' # Empty for console outpyut
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO # WARNING, ERROR, CRITICAL

logging.basicConfig(
    level=LOG_LEVEL,
    filename=LOG_PATH,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s'
)
