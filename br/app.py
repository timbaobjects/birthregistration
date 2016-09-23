#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import calendar
from datetime import datetime, date
import logging
import re
# requires python-dateutil to work
try:
    from dateutil.parser import *
    from dateutil.relativedelta import relativedelta
except ImportError:
    raise ImportError('python-dateutil is required for this app to work.')
from rapidsms.apps.base import AppBase
from models import BirthRegistration
from reporters.models import PersistantConnection, Reporter, Role
from locations.models import Location
from .grammars import parse_date, parse_report

MAX_REPORT_WINDOW = 90 * 3600 * 24  # reports older than 90 days from the day of submission will be rejected
logger = logging.getLogger(__name__)


class BirthRegistrationApp(AppBase):

    error_msgs = {
        'invalid_location': "Sorry, I don't know any location with the code: {}. You sent: {}",
        'invalid_role': "Unknown role code: {}. You sent: {}",
        'unauthorized_reporter': 'Please register your number with RapidSMS before sending this report',
        'unauthorized_role': 'You are not authorized to send this report.',
        'invalid_date': 'An invalid date was found in your report. Date format should be DD/MM/YYYY. You sent: {}',
        'invalid_report': 'I don\'t understand the report you sent. You sent: {}',
        }
    response_msgs = {
        'help': "['report', 'register']",
        'registered': 'Hello {name}! You are now registered as {role} at {location_name} {location_type}.',
        'already_registered': 'Hello again {name}! You are already registered as a {role} at {location_name}.',
        'report': "{date} BR report: Girls below 1={g1}, 1-4={g4}, 5-9={g9}, 10-17={g18}, Boys below 1={b1}, 1-4={b4}, 5-9={b9}, 10-17={b18} for {location}",
    }

    prefix = re.compile('^\s*(?:br)(?:[\s,;:]*)(?P<parts>.*)$', re.IGNORECASE)
    register_pattern = re.compile('^register (?P<location_code>\d+) (?P<role>[a-z0-9_]+) (?P<name>.*)$', re.IGNORECASE)
    report_pattern = re.compile('^report (?P<gender_data>.*)$', re.IGNORECASE)
    date_pattern = re.compile(r"(?P<date>(\d+[\/\-]\d+|\d+[\/\-]\d+[\/\-]\d+))$")

    # the reason we're using two regexes instead of one is because we want to
    # know when someone has actually entered an invalid date. if we use just
    # one, a last value like '12-12' would assign the current date to the
    # report, and that is not what we want.
    strict_date_pattern = re.compile(r"(?P<date>(\d{2}[\/\-]\d{2}[\/\-]\d{4}))$")

    def parse(self, msg):
        conn = PersistantConnection.from_message(msg)
        msg.persistant_connection = conn
        msg.reporter = conn.reporter

        if msg.reporter:
            msg.persistance_dict = {"reporter": msg.reporter}
        else:
            msg.persistance_dict = {"connection": msg.persistant_connection}

        # log, whether we know who the sender is or not
        if msg.reporter:
            logger.info("Identified: %s as %r" % (conn, msg.reporter))
        else:
            logger.info("Unidentified: %s" % (conn))

        # update last_seen, which automatically
        # populates the same property
        conn.seen()

    def parse_date(self, message):
        '''The purpose of this method is to look for any strings resembling
        a date string eg. 7/12/2009, 7/12, 7-12-2009, 7-12, etc and use that
        to configure the date of the message. This is essentially to cater for
        reports that may come in late.'''
        msg_date = None
        try:
            msg_date = parse_date(message.text)
        except ValueError:
            message.respond(self.error_msgs['invalid_date'].format(message.text))
            return False

        moment = datetime.now()
        if not msg_date:
            if ('-' not in message.text) and ('/' not in message.text):
                # sender never tried to specify a date
                msg_date = moment
            else:
                # sender tried to specify a date, but it was invalid
                message.respond(self.error_msgs['invalid_date'].format(message.text))
                return False
        
        if msg_date <= moment:
            date_diff = moment - msg_date
            if abs(date_diff.total_seconds()) > MAX_REPORT_WINDOW:
                message.respond(self.error_msgs['invalid_date'].format(message.text))
                return False

            logger.info("setting message date to %s" % msg_date)
            message.datetime = self._classify_date(msg_date)

            # Remove date from message
            if ('-' in message.text) or ('/' in message.text) or ('\\' in message.text):
                logger.info("previous message: %s" % message.text.strip())
                msgtxt = " ".join(re.split("\s+", message.text.strip())[0:-1])
                message.text = msgtxt
                logger.info("new message: %s" % message.text)
            return True
        else:
            message.respond(self.error_msgs['invalid_date'].format(message.text))
            return False

    def handle(self, message):
        try:
            match = self.prefix.match(message.text)
            if match:
                # parse and extract any specified dates
                status = self.parse_date(message)
                if not status:
                    # invalid date message has been sent
                    return True

                m = self.register_pattern.match(match.group('parts'))
                if m:
                    self.register(message, **m.groupdict())
                    return True
                m = self.report_pattern.match(match.group('parts'))
                if m:
                    self.report(message, **m.groupdict())
                    return True

                self.help(message)
                return True
        except Exception, e:
            logger.error(e)

    def help(self, message):
        message.respond(self.response_msgs['help'])

    def register(self, message, location_code, role, name=''):
        data = {}
        try:
            data['location'] = Location.objects.get(code=location_code)
            data['role'] = Role.objects.get(code__iexact=role)
            data['alias'], data['first_name'], data['last_name'] = Reporter.parse_name(name.strip())
            rep = Reporter(**data)
            conn = PersistantConnection.from_message(message)
            if Reporter.exists(rep, conn):
                message.respond(self.response_msgs['already_registered'].format(
                    name=rep.first_name,
                    role=rep.role,
                    location_name=rep.location))
                return True

            rep.save()
            conn.reporter = rep
            conn.save()

            message.respond(self.response_msgs['registered'].format(
                            name=rep.first_name,
                            role=rep.role,
                            location_name=rep.location,
                            location_type=rep.location.type))
        except Role.DoesNotExist:
            message.respond(self.error_msgs['invalid_role'].format(role, message.text))
        except Location.DoesNotExist:
            message.respond(self.error_msgs['invalid_location'].format(location_code, message.text))

        return True

    def report(self, message, gender_data):
        # report = self._parse_gender_data(gender_data)
        report = parse_report(message.text)

        if not report:
            message.respond(self.error_msgs['invalid_report'].format(message.text))
            return True

        try:
            if not hasattr(message, 'reporter') or not message.reporter:
                message.respond(self.error_msgs['unauthorized_reporter'])
                return True

            if not message.reporter.role.code.lower() in ['br']:
                message.respond(self.error_msgs['unauthorized_role'])
                return True

            location = message.reporter.location

            # store the report
            try:
                br = BirthRegistration.objects.get(
                    connection=PersistantConnection.from_message(message),
                    reporter=message.reporter,
                    location=location,
                    time=message.datetime)
            except BirthRegistration.DoesNotExist:
                br = BirthRegistration()
                br.connection = PersistantConnection.from_message(message)
                br.reporter = message.reporter
                br.location = location
                br.time = message.datetime

            br.girls_below1 = report['female'].get(1)
            br.girls_1to4 = report['female'].get(2)
            br.girls_5to9 = report['female'].get(3)
            br.girls_10to18 = report['female'].get(4)
            br.boys_below1 = report['male'].get(1)
            br.boys_1to4 = report['male'].get(2)
            br.boys_5to9 = report['male'].get(3)
            br.boys_10to18 = report['male'].get(4)

            br.save()

            # respond adequately
            message.respond(self.response_msgs['report'].format(
                location=location.name,
                date=message.datetime.strftime('%d/%m/%Y'),
                g1=br.girls_below1,
                g4=br.girls_1to4,
                g9=br.girls_5to9,
                g18=br.girls_10to18,
                b1=br.boys_below1,
                b4=br.boys_1to4,
                b9=br.boys_5to9,
                b18=br.boys_10to18))
        except Exception, e:
            logger.debug(e)

        return True

    def _parse_gender_data(self, s):
        ''' parser for the gender data submitted
        by the birth registrars
        gender_data         ::= number
        gender_male         ::= M|m|B|b
        gender_female       ::= F|f|G|g
        gender_submission   ::= (gender_male|gender_female) gender_data*
        submitted_data      ::= gender_submission*'''

        male_re = re.compile(r'^(m|b).*', re.I)
        female_re = re.compile(r'^(f|g).*', re.I)

        in_data = ''
        gender_data = {'male': {}, 'female': {}}
        counter = 0
        gen = s.split()
        for token in gen:
            if male_re.match(token):
                in_data = 'male'
                counter = 1
                continue
            if female_re.match(token):
                in_data = 'female'
                counter = 1
                continue
            if token.isdigit() and in_data:
                gender_data[in_data][counter] = int(token)
                counter += 1

        return gender_data

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
