# -*- coding: utf-8 -*-
from unittest import TestCase

from handlers.fuzzy import FuzzySubKeywordHandler


class FuzzySubKeywordHandlerTest(TestCase):
    def setUp(self):
        FuzzySubKeywordHandler.keyword = u'TEST'
        FuzzySubKeywordHandler.subkeywords = [u'first', u'second']

        self.help_response = u'Please send {} *KEYWORD* to get help on *KEYWORD*'.format(
            FuzzySubKeywordHandler.keyword)

        self.canned_responses = {
            keyword: u'This is the response for the "{}" subkeyword'.format(
                keyword) for keyword in FuzzySubKeywordHandler.subkeywords
        }

        FuzzySubKeywordHandler.handle_first = lambda handler, text: handler.respond(
            self.canned_responses[u'first'])
        FuzzySubKeywordHandler.handle_second = lambda handler, text: handler.respond(
            self.canned_responses[u'second'])

    def test_help_message(self):
        responses = FuzzySubKeywordHandler.test(FuzzySubKeywordHandler.keyword)
        self.assertTrue(responses)
        self.assertEqual(responses[0], self.help_response)

        responses = FuzzySubKeywordHandler.test(
            u'{} '.format(FuzzySubKeywordHandler.keyword))
        self.assertEqual(responses[0], self.help_response)

    def test_exact_keyword_match(self):
        test_keyword = FuzzySubKeywordHandler.subkeywords[0]

        responses = FuzzySubKeywordHandler.test(u'{} {}'.format(
            FuzzySubKeywordHandler.keyword, test_keyword))
        self.assertTrue(responses)
        self.assertEqual(responses[0], self.canned_responses[test_keyword])

    def test_good_inexact_keyword_match(self):
        test_keyword = u'fir'

        responses = FuzzySubKeywordHandler.test(u'{} {}'.format(
            FuzzySubKeywordHandler.keyword, test_keyword))
        self.assertTrue(responses)
        self.assertEqual(responses[0], self.canned_responses[u'first'])

    def test_poor_inexact_keyword_match(self):
        test_keyword = u'fur'

        responses = FuzzySubKeywordHandler.test(u'{} {}'.format(
            FuzzySubKeywordHandler.keyword, test_keyword))
        self.assertTrue(responses)
        self.assertEqual(responses[0], self.help_response)
