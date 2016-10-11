# -*- coding: utf-8 -*-
from unittest import TestCase

from handlers.fuzzy import FuzzySubKeywordHandler


class FuzzySubKeywordHandlerTest(TestCase):
    def setUp(self):
        FuzzySubKeywordHandler.keyword = u'TEST'
        self.help_response = u'Please send {} *KEYWORD* to get help on *KEYWORD*'.format(
            FuzzySubKeywordHandler.keyword)

    def test_help_message(self):
        responses = FuzzySubKeywordHandler.test(FuzzySubKeywordHandler.keyword)
        self.assertTrue(responses)
        self.assertEqual(responses[0], self.help_response)
