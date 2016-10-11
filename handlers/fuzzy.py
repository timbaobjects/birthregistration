# -*- coding: utf-8 -*-
from fuzzywuzzy import process
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler


class FuzzySubKeywordHandler(KeywordHandler):
    '''Keyword handler that allows fuzzy subkeyword matching.'''

    help_text = u'Please send {keyword} *KEYWORD* to get help on *KEYWORD*'

    def handle(self, text):
        pass

    def help(self):
        if self.help_text:
            response = self.help_text.format(keyword=self.keyword)
        else:
            response = u'No help defined'

        self.respond(response)
