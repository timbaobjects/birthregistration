# -*- coding: utf-8 -*-
# Contains the implementation of FuzzySubKeywordAppBase, a customized
# RapidSMS app that uses fuzzywuzzy for fuzzy subkeyword matching
# once a keyword has been matched
import re

from fuzzywuzzy import process
from rapidsms.apps.base import AppBase

from reporters.models import PersistantConnection


class FuzzySubKeywordAppBase(AppBase):
    '''
    Base fuzzy subkeyword matching app.

    Subclasses should have the following attributes/methods:
    - keyword (string): the keyword for the app
    - subkeyword (a list of strings): a list of subkeywords that
      will be matched against
    - min_ratio (integer ranged 0-100): a minimum match ratio below
      which the fuzzy matching will fail. a lower ratio allows for
      a more inexact match. a value of 70 is recommended
    - handle_* methods: for each subkeyword, there must be a matching
      handle_<subkeyword> method taking the following arguments:
        -> self: this goes without saying
        -> message (a RapidSMS Message instance): the original Message
           passed to the app `handle()` method. The method can reply the
           inbound message using this
        -> message_text (string): the message text after both keyword,
           subkeyword and leading and trailing spaces have been removed
    - help: a method taking the original RapidSMS Message instance
      (so the method can respond to the message) for providing generic help
    '''
    def parse(self, message):
        connection = PersistantConnection.from_message(message)
        message.persistant_connection = connection
        message.reporter = connection.reporter

        if message.reporter:
            message.persistance_dict = {u'reporter': message.reporter}
        else:
            message.persistance_dict = {u'connection': message.connection}

        # mark connection as seen
        connection.seen()

    def handle(self, message):
        text = message.text.lower().strip()

        if text.startswith(self.keyword.lower()):
            try:
                text = re.sub(self.keyword, u'', message.text, count=1,
                    flags=re.I)
                parts = text.split(None, 1)
            except ValueError:
                self.help(message)
                return True

            if len(parts) == 0:
                # sender only sent keyword
                self.help(message)
                return True
            elif len(parts) == 1:
                # sender sent keyword and subkeyword only
                subkeyword = parts[0]
                message_text = u''
            else:
                subkeyword, message_text = parts

            # do fuzzy matching on the subkeyword
            result = process.extractOne(subkeyword, self.subkeywords,
                score_cutoff=self.min_ratio)
            if result is None:
                # no subkeywords were matched
                self.help(message)
                return True

            matched_subkeyword, score = result
            handler = getattr(self, u'handle_{}'.format(matched_subkeyword))
            handler(message, message_text)
            return True

        # message was not processed
        return False
