# Kjernekar - a KJ-team slack-bot
A bot for slack with custom features for the KJ-team, inspired by the haikubot by karl-run. 


## Context management
This slackbot is based on a simple concept of recognizing special words or phrases in a message to set the context of a message. Then respond to this context with one or more possible responses.

The phrases defining a context is stored in a .context file while all possible responses to the context is stored in a .response file.

### Customized response
The response can contain placeholders for the sender or target of the message (or reaction). The current placeholders are:
- {sender}
- {target}
- {botname}
