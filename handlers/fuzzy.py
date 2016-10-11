# -*- coding: utf-8 -*-
from fuzzywuzzy import process
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler


class FuzzySubKeywordHandler(KeywordHandler):
    '''Keyword handler that allows fuzzy subkeyword matching.'''
    min_ratio = 70
    help_text = u'Please send {keyword} *KEYWORD* to get help on *KEYWORD*'
    subkeywords = []

    def handle(self, text):
        try:
            parts = text.split(None, 1)
        except ValueError:
            self.respond(self.help_text)
            return

        if len(parts) == 1:
            subkeyword = parts[0]
            message = u''
        else:
            subkeyword, message = parts

        result, ratio = process.extractOne(subkeyword, self.subkeywords)
        if ratio < self.min_ratio:
            self.help()
            return

        handler_name = u'handle_{}'.format(result)
        handler = getattr(self, handler_name)

        handler(message)


    def help(self):
        if self.help_text:
            response = self.help_text.format(keyword=self.keyword)
        else:
            response = u'No help defined'

        self.respond(response)
