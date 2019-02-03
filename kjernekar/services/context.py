import logging
from enum import Enum, auto

from pkg_resources import resource_string, resource_listdir

class Context(Enum):
    # Chat context
    PUNISH = auto()
    SCORE = auto()
    GREETING = auto()
    # BOT response context
    DONTPUNISHME = auto()
    GRATEFUL = auto()


    def incontext(self, sentence):
        EMPTY = '{empty}'
        if sentence == None:
            return False

        contextfile = resource_string('kjernekar.services.contextfiles', '{}.context'.format(self.name)).decode('utf-8')
        triggerwords = filter(None, [context.strip() for context in contextfile.split('\n')])
        for triggerword in triggerwords:
            if triggerword.replace(EMPTY,'').lower() in sentence.lower():
                return True
        return False

if __name__ == "__main__":
    # Should trigger GREETING true
    print(Context.GREETING.incontext('Kjernekar er du der?'))
    print(Context.GREETING.incontext('Er du der Kjernekar?'))
    print(Context.GREETING.incontext('Hei Kjernekar!'))
    print(Context.GREETING.incontext('Hallo Kjernekar'))

    # Should trigger GREETING false
    print(Context.GREETING.incontext('Dumming Kjernekar'))
    print(Context.GREETING.incontext('Kjernekar er feit'))
