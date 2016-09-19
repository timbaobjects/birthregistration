from __future__ import unicode_literals

import calendar
from datetime import date, datetime
import re
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler

from dateutil.relativedelta import relativedelta

from reporters.models import PersistantConnection

from ..grammars import parse_date

MAX_REPORT_WINDOW = 3600 * 24 * 90  # reports older than 90 days from submission date will be rejected
REGISTERED_KEYWORDS = set()


class HandlerMeta(type):
    def __new__(metaclass, cls, parents, attrs):
        if 'keyword' in attrs:
            REGISTERED_KEYWORDS.add(attrs['keyword'])
        return type.__new__(metaclass, cls, parents, attrs)


class PrefixHandler(KeywordHandler):
    __metaclass__ = HandlerMeta
    prefix = 'sub'

    error_msgs = {
        'invalid_location': "ERROR: Sorry, I don't know any location with the code: {}. You sent: {}",
        'invalid_role': "ERROR: Unknown role code: {}. You sent: {}",
        'unauthorized_reporter': 'ERROR: Please register your number with RapidSMS before sending this report',
        'unauthorized_role': 'ERROR: You are not authorized to send this report.',
        'invalid_date': 'ERROR: An invalid date was found in your report. Date format should be DD/MM/YYYY. You sent: {}',
        'invalid_report': 'ERROR: I don\'t understand the report you sent. You sent: {}',
    }
    response_msgs = {
        'help': "['report', 'register']",
        'registered': 'Hello {name}! You are now registered as {role} at {location_name} {location_type}.',
        'already_registered': 'Hello again {name}! You are already registered as a {role} at {location_name}.',
        'report': "{date} BR report: Girls below 1={g1}, 1-4={g4}, 5-9={g9}, 10-17={g18}, Boys below 1={b1}, 1-4={b4}, 5-9={b9}, 10-17={b18} for {location}",
    }

    @classmethod
    def _keyword(cls):
        if hasattr(cls, 'keyword') and cls.keyword:
            pattern = r"^\s*(?:%s)\s*(?:%s)(?:[\s,;:]+(.+))?$" % (cls.prefix, cls.keyword)
        else:
            pattern = r"^\s*(?:%s)(\s*?)$" % cls.prefix
        return re.compile(pattern, re.IGNORECASE)

    def _classify_date(self, message_date):
        month_end = calendar.monthrange(message_date.year, message_date.month)[1]
        if message_date.day < 15:
            return date(
                message_date.year,
                message_date.month,
                month_end) + relativedelta(months=-1)
        elif month_end > message_date.day >= 15:
            return date(
                message_date.year,
                message_date.month,
                15)
        else:
            return message_date.date()

    def preprocess(self):
        conn = PersistantConnection.from_message(self.msg)
        self.msg.persistant_connection = conn
        self.msg.reporter = conn.reporter

        if self.msg.reporter:
            self.msg.persistance_dict = {"reporter": self.msg.reporter}
        else:
            self.msg.persistance_dict = {"connection": self.msg.persistant_connection}

        # log, whether we know who the sender is or not
        if self.msg.reporter:
            self.info("Identified: %s as %r" % (conn, self.msg.reporter))
        else:
            self.info("Unidentified: %s" % (conn))

        # update last_seen, which automatically
        # populates the same property
        conn.seen()

    def update_message_date(self, text):
        msg_date = None
        try:
            msg_date = parse_date(text)
        except ValueError:
            self.respond(PrefixHandler.error_msgs['invalid_date'].format(text))
            return False

        moment = datetime.now()
        if not msg_date:
            if ('-' not in text) and ('/' not in text):
                # sender didn't try to specify a date
                msg_date = moment
            else:
                # sender tried to specify a date, but it was invalid
                self.respond(PrefixHandler.error_msgs['invalid_date'].format(text))
                return False

        if msg_date <= moment:
            difference = msg_date - moment
            if abs(difference.total_seconds()) >= MAX_REPORT_WINDOW:
                self.respond(PrefixHandler.error_msgs['invalid_date'].format(text))
                return False

            self.info('Setting message date to {}'.format(msg_date))
            self.msg.datetime = self._classify_date(msg_date)

            # if the user specified the date in the message,
            # it should have come last and should be stripped out
            if ('-' in text) or ('/' in text) or ('\\' in text):
                self.info('previous message: {}'.format(text.strip()))
                msgtxt = ' '.join(re.split('\s+', text.strip())[:-1])
                self.cleaned_message = msgtxt
                self.info('new message: {}'.format(msgtxt))
            else:
                self.cleaned_message = text
            return True
        else:
            self.respond(PrefixHandler.error_msgs['invalid_date'].format(text))
            return False

    def help(self):
        if hasattr(self, 'help_text') and self.help_text:
            self.respond(self.help_text)
        else:
            self.respond(PrefixHandler.response_msgs['help'])
