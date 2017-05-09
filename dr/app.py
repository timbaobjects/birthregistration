# -*- coding: utf-8 -*-
import calendar
from datetime import date
import re

from django.utils.translation import ugettext as _
from fuzzywuzzy import process
import parsley

from common.fuzzyapp.base import FuzzySubKeywordAppBase
from common.utilities import getConnectionAndReporter
from dr.models import FIELD_MAP, DeathReport
from locations.models import Location
from reporters.models import PersistantConnection, Reporter, Role


reg_grammar = parsley.makeGrammar('''
register = <digit+>:location_code ws <letterOrDigit+>:role_code ws <anything*>:full_name -> (location_code, role_code, full_name)
''', {})

report_grammar_text = u'''
entry = ({}):field_name ws <digit+>:value ws -> (field_name, int(value))
entry_list = entry+
report = entry_list:entries -> entries
'''.format(u'|'.join(u"'{}'".format(key) for key in FIELD_MAP.keys()))

report_grammar = parsley.makeGrammar(report_grammar_text, {})

ERROR_MESSAGES = {
    u'not_registered': _(u'Please register your number with RapidSMS before sending this report'),
    u'invalid_location': _(u'You sent an incorrect location code: %(location_code)s. You sent: %(text)s'),
    u'invalid_role': _(u'You sent an incorrect role code: %(role_code)s. You sent: %(text)s'),
    u'invalid_message': _(u'Your message is incorrect. Please send DR HELP for help. You sent: %(text)s'),
    u'unauthorized_role': _(u'You are not authorized to send this report.'),
}

HELP_MESSAGES = {
    None: _(u'Send DR HELP REGISTER for registration help. Send DR HELP REPORT for report help.'),
    u'register': _(u'Send DR REGISTER location-code role-code full-name.'),
    u'report': _(u'Please consult your training manual for how to send your report.'),
}

RESPONSE_MESSAGES = {
    u'register': _(u'Hello %(name)s! You are now registered as %(role)s at %(location)s %(location_type)s'),
    u'report': _(u'Thank you %(name)s. Received DR report for %(location)s %(location_type)s for %(date)s'),
    u'already_registered': _(u'Hello again %(name)s. You are already registered as a %(role)s at %(location)s %(location_type)s.'),
}


def classify_date(dt):
    if dt.day <= 7:
        if dt.month == 1:
            report_month = 12
            report_year = dt.year - 1
        else:
            report_month = dt.month - 1
            report_year = dt.year
    else:
        report_month = dt.month
        report_year = dt.year

    report_day = 1

    report_date = date(report_year, report_month, report_day)

    return report_date



class DeathRegistrationApp(FuzzySubKeywordAppBase):
    keyword = u'dr'
    subkeywords = [u'help', u'register', u'report']
    min_ratio = 70

    ALLOWED_ROLE_CODES = [u'dr']

    def handle_help(self, message, message_text):
        text = message_text.strip()

        if text == u'':
            message.respond(HELP_MESSAGES[None])
            return

        key = process.extractOne(text, self.subkeywords, score_cutoff=50)
        if key is None:
            message.respond(HELP_MESSAGES[None])
            return

        message.respond(HELP_MESSAGES[key[0]])

    def handle_register(self, message, message_text):
        connection, unused = getConnectionAndReporter(message,
            self.ALLOWED_ROLE_CODES)
        text = message_text.strip()

        if text == u'':
            message.respond(HELP_MESSAGES[u'register'])
            return

        try:
            location_code, role_code, full_name = reg_grammar(text).register()
        except parsley.ParseError:
            message.respond(ERROR_MESSAGES[u'invalid_message'] % {
                u'text': message.text})
            return

        location = Location.get_by_code(location_code)
        if location is None:
            message.respond(ERROR_MESSAGES[u'invalid_location'] % {
                u'location_code': location_code, u'text': message.text})
            return

        role = Role.get_by_code(role_code)
        if role is None:
            message.respond(ERROR_MESSAGES[u'invalid_role'] % {
                u'role_code': role_code, u'text': message.text})
            return

        if role.code.lower() not in self.ALLOWED_ROLE_CODES:
            message.respond(ERROR_MESSAGES[u'invalid_role'] % {
                u'role_code': role_code, u'text': message.text})
            return

        kwargs = {u'location': location, u'role': role}
        kwargs[u'alias'], kwargs[u'first_name'], kwargs[u'last_name'] = Reporter.parse_name(full_name)
        rep = Reporter(**kwargs)

        if Reporter.exists(rep, connection):
            message.respond(RESPONSE_MESSAGES[u'already_registered'] % {
                u'name': rep.first_name, u'role': rep.role.name,
                u'location': rep.location.name,
                u'location_type': rep.location.type.name})
            return

        rep.save()
        connection.reporters.add(rep)

        message.respond(RESPONSE_MESSAGES[u'register'] % {u'name': rep.first_name,
            u'role': rep.role.code, u'location': rep.location.name,
            u'location_type': rep.location.type.name})

    def handle_report(self, message, message_text):
        connection, reporter = getConnectionAndReporter(message,
            self.ALLOWED_ROLE_CODES)
        text = message_text.strip().upper()

        if text == u'':
            message.respond(HELP_MESSAGES[u'report'])
            return

        if reporter is None:
            message.respond(ERROR_MESSAGES[u'not_registered'])
            return

        try:
            entries = report_grammar(text).report()
        except parsley.ParseError:
            message.respond(ERROR_MESSAGES[u'invalid_message'] % {
                u'text': message.text})
            return

        location = reporter.location

        report_data = {k: 0 for k in FIELD_MAP}
        report_data.update(dict(entries))

        report_date = classify_date(date.today())
        try:
            report = DeathReport.objects.get(date=report_date, location=location)
        except DeathReport.DoesNotExist:
            report = DeathReport(location=location, date=report_date,
            connection=connection,
            reporter=reporter)

        report.data.update(report_data)
        report.save()

        message.respond(RESPONSE_MESSAGES[u'report'] % {
            u'location': location.name, u'location_type': location.type.name,
            u'name': reporter.first_name,
            u'date': report.date.strftime(u'%d-%m-%Y')})

    def help(self, message):
        message.respond(HELP_MESSAGES[None])
