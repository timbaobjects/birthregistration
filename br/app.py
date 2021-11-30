#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import calendar
from datetime import datetime, date, timedelta
from django.utils.translation import ugettext as _
import logging
import parsley
import re
import sys
import unicodedata
# requires python-dateutil to work
try:
    from dateutil.parser import parse
    from dateutil.relativedelta import relativedelta
except ImportError:
    raise ImportError('python-dateutil is required for this app to work.')

from rapidsms.apps.base import AppBase

from br.models import BirthRegistration
from common.utilities import getConnectionAndReporter
from reporters.models import Reporter, Role
from locations.models import Location

MAX_REPORT_WINDOW = 180 * 24 * 3600  # reports older than 180 days from the day of submission will be rejected
ALLOWED_PUNCTUATIONS = [u'/', u'-']
logger = logging.getLogger(__name__)
help_grammar = parsley.makeGrammar('''
    help = 'br' ws 'help' ws <letter*>:selector -> (selector)
''', {})
br_grammar = parsley.makeGrammar('''
    parameter = <digit+>:datum ws -> datum
    male_report = ('m' | 'b'):gender ws <parameter{1,4}>:data -> ('m', data.strip().split(' '))
    female_report = ('f' | 'g'):gender ws <parameter{1,4}>:data -> ('f', data.strip().split(' '))
    report = 'br' ws 'report' ws (male_report | female_report){1,2}:gender_report -> (gender_report)
    register = 'br' ws 'register' ws <digit+>:location_code ws <letterOrDigit+>:role ws <anything*>:name -> (location_code, role, name)
''', {})

ALLOWED_ROLE_CODES = [u'br']

tbl = dict.fromkeys((i for i in xrange(sys.maxunicode)
        if unicodedata.category(unichr(i)).startswith('P')
        and i not in map(ord, ALLOWED_PUNCTUATIONS)), u' ')


def remove_punctuation(text):
    return unicode(text.replace('\\', '/')).translate(tbl).replace('\\', '/')


class BirthRegistrationApp(AppBase):
    error_messages = {
        'invalid_location': _("You sent an incorrect location code: %(location_code)s. You sent: %(text)s"),
        'invalid_role': _("Unknown role code: %(role_code)s. You sent: %(text)s"),
        'unauthorized_reporter': _("Please register your number with RapidSMS before sending this BR report."),
        'unauthorized_role': _('You are not authorized to send this report.'),
        'invalid_date': _("You used an incorrect date in your report. Your date should be in the format DD/MM/YYYY. You sent: %(text)s"),
        'early_report': _("You used an incorrect date in your report. You can't send a report earlier than %(early_date)s. You sent: %(text)s"),
        'future_report': _("You used an incorrect date in your report. You can't send a report for a date in the future. You sent: %(text)s"),
        'invalid_message': _("Your message is incorrect. Please send BR HELP for help on sending a report. You sent: %(text)s"),
        'inactive_location': _("You are registered at a location marked as inactive. Please contact your supervisor"),
    }
    help_messages = {
        'general': _("For help on BR reports, reply: BR HELP REPORT. For help on registration, reply: BR HELP REGISTER"),
        'report': _("To send BR report, send BR REPORT B #under_1 #1_to_4 #5_to_9 #10_to_17 G #under_1 #1_to_4 #5_to_9 #10_to_17"),
        'register': _("To register, send BR REGISTER location_code BR full_name"),
    }
    response_messages = {
        'registered': _("Hello %(name)s! You are now registered as %(role)s at %(location_name)s %(location_type)s."),
        'already_registered': _("Hello again %(name)s! You are already registered as a %(role)s at %(location_name)s."),
        'report': _("Thank you for your BR report. Girls <1=%(girls_below1)d, 1-4=%(girls_1to4)d, 5-9=%(girls_5to9)d, 10+=%(girls_10to18)d; Boys <1=%(boys_below1)d, 1-4=%(boys_1to4)d, 5-9=%(boys_5to9)d, 10+=%(boys_10to18)d sent %(date)s for %(location)s"),
    }

    prefix = re.compile('^\s*(?:br)(?:[\s,;:]*)(?P<parts>.*)$', re.IGNORECASE)
    date_expression = re.compile('(?P<text>.+)\s(?P<date>\d{1,2}[\/\-]\d{1,2}([\/\-]\d{2,4})?)?$')

    def handle(self, message):
        try:
            # strip whitespace and delete punctuations
            text_message = remove_punctuation(message.text.lower().strip())
            if text_message.startswith('br'):
                now = date.today()
                # parse and extract any specified dates
                search_query = re.search(self.date_expression, text_message)
                if search_query:
                    message_parts = search_query.groups()
                    # a date string was found in the text
                    try:
                        message_date = parse(message_parts[1], dayfirst=True).date()
                        text_message = message_parts[0]
                    except ValueError:
                        message.respond(self.error_messages['invalid_date'] % dict(text=message.text))
                        return True
                else:
                    message_date = now

                if message_date <= now:
                    time_diff = now - message_date
                    oldest_date = now - timedelta(0, MAX_REPORT_WINDOW)
                    if time_diff.total_seconds() > MAX_REPORT_WINDOW:
                        message.respond(self.error_messages['early_report'] % dict(text=message.text, early_date=oldest_date.strftime('%d/%m/%Y')))
                        return True

                    logger.info('setting message date to %s' % message_date)
                    message.datetime = self._classify_date(message_date)
                else:
                    message.respond(self.error_messages['future_report'] % dict(text=message.text))
                    return True

                try:
                    if help_grammar(text_message).help() != None:
                        self.help(message)
                        return True
                except parsley.ParseError:
                    pass

                try:
                    registration_data = br_grammar(text_message).register()
                    if registration_data:
                        self.register(
                            message,
                            registration_data[0],
                            registration_data[1],
                            registration_data[2].upper())
                        return True
                except parsley.ParseError:
                    pass

                try:
                    br_data = br_grammar(text_message).report()
                    if br_data:
                        self.report(message, br_data)
                        return True
                except parsley.ParseError:
                    message.respond(self.error_messages['invalid_message'] % dict(text=message.text))
                    return True

                self.help(message)
                return True
        except Exception as e:
            logger.error(e)

    def help(self, message):
        text_message = message.text.lower().strip()
        try:
            selector = help_grammar(text_message).help()
            if selector == 'register':
                return message.respond(self.help_messages['register'])
            elif selector == 'report':
                return message.respond(self.help_messages['report'])
        except parsley.ParseError:
            pass

        return message.respond(self.help_messages['general'])

    def register(self, message, location_code, role, name=''):
        conn, unused = getConnectionAndReporter(message, ALLOWED_ROLE_CODES)

        data = {}
        try:
            data['location'] = Location.objects.get(code=location_code,
                type__name=u'RC', active=True)
            data['role'] = Role.objects.get(code__iexact=role)
            data['alias'], data['first_name'], data['last_name'] = Reporter.parse_name(name.strip())
            rep = Reporter(**data)

            if Reporter.exists(rep, conn):
                message.respond(self.response_messages['already_registered'] % dict(
                    name=rep.first_name,
                    role=rep.role,
                    location_name=rep.location))
                return True

            rep.save()
            conn.reporters.add(rep)

            message.respond(self.response_messages['registered'] % dict(
                name=rep.first_name,
                role=rep.role,
                location_name=rep.location,
                location_type=rep.location.type))
        except Role.DoesNotExist:
            message.respond(self.error_messages['invalid_role'] % dict(role_code=role, text=message.text))
        except Location.DoesNotExist:
            message.respond(self.error_messages['invalid_location'] % dict(location_code=location_code, text=message.text))

        return True

    def report(self, message, gender_data):
        connection, reporter = getConnectionAndReporter(message, ALLOWED_ROLE_CODES)

        report = dict(gender_data)
        for gender in ['m', 'f']:
            report[gender] = map(lambda i: int(i), report[gender]) + ([0] * (4 - len(report[gender]))) if report[gender] else [0, 0, 0, 0]

        try:
            if reporter is None:
                message.respond(self.error_messages['unauthorized_reporter'])
                return True

            if not reporter.role.code.lower() in ALLOWED_ROLE_CODES:
                message.respond(self.error_messages['unauthorized_role'])
                return True

            location = reporter.location
            if not location.active:
                message.respond(self.response_messages['inactive_location'])
                return True

            # store the report
            try:
                br = BirthRegistration.objects.get(
                    connection=connection,
                    reporter=reporter,
                    location=location,
                    time=message.datetime)
            except BirthRegistration.DoesNotExist:
                br = BirthRegistration()
                br.connection = connection
                br.reporter = reporter
                br.location = location
                br.time = message.datetime

            br.girls_below1 = report['f'][0]
            br.girls_1to4   = report['f'][1]
            br.girls_5to9   = report['f'][2]
            br.girls_10to18 = report['f'][3]
            br.boys_below1  = report['m'][0]
            br.boys_1to4    = report['m'][1]
            br.boys_5to9    = report['m'][2]
            br.boys_10to18  = report['m'][3]

            br.save()

            # respond adequately
            message.respond(self.response_messages['report'] % dict(
                location=location.name,
                date=message.datetime.strftime('%d/%m/%Y'),
                girls_below1=br.girls_below1,
                girls_1to4=br.girls_1to4,
                girls_5to9=br.girls_5to9,
                girls_10to18=br.girls_10to18,
                boys_below1=br.boys_below1,
                boys_1to4=br.boys_1to4,
                boys_5to9=br.boys_5to9,
                boys_10to18=br.boys_10to18))
        except Exception as e:
            logger.debug(e)

        return True

    def _classify_date(self, message_date):
        if message_date.day < 15:
            # for days less than the 15th, return the last day of the
            # previous month
            prev_month_date = message_date + relativedelta(months=-1)
            prev_month_last_day = calendar.monthrange(prev_month_date.year,
                prev_month_date.month)[1]
            return date(prev_month_date.year, prev_month_date.month,
                prev_month_last_day)
        else:
            month_last_day = calendar.monthrange(message_date.year,
                message_date.month)[1]
            if month_last_day > message_date.day >= 15:
                # if the day is greater than or equal to the 15th,
                # but not equal to the last day of the current month,
                # set it to the 15th of the current month
                return date(message_date.year, message_date.month, 15)
            else:
                # else, it's the last day of the month, so return the
                # same date
                return message_date
