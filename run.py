from kjernekar import config
from kjernekar.bot import Kjernekar

if __name__ == "__main__":
    bot = Kjernekar(config.SLACK_API_TOKEN)
    try:
        bot.run()
    except Exception as err:
        bot.clean_up()
        raise err
