# -*- coding: utf-8 -*-
import logging
import re

from django.utils.translation import ugettext as _
from django.utils.timezone import now
from fuzzywuzzy import process
import parsley
from rapidsms.apps.base import AppBase

from common.utilities import getConnectionAndReporter
from ipd.models import NonCompliance, Report, Shortage
from locations.models import Location
from reporters.models import PersistantConnection, Reporter, Role

commodity_codes = [choice[0] for choice in Report.IM_COMMODITIES]
reason_codes = [choice[0] for choice in NonCompliance.NC_REASONS]

logger = logging.getLogger(__name__)

grammar = parsley.makeGrammar('''
commodity_code = <letterOrDigit+>:code -> code
commodity_amt_pair = commodity_code:code ws <digit+>:amt -> (code, int(amt))
shortage_list_item = commodity_code:code ws -> code
report_list_item = commodity_amt_pair:pair ws -> pair
shortage_list = shortage_list_item+
report_list = report_list_item+
noncompliance = <digit+>:location_code ws <digit>:reason_code ws <digit+>:cases -> (location_code, reason_code, int(cases))
register = <digit+>:location_code ws <letterOrDigit+>:role_code ws <anything*>:full_name -> (location_code, role_code, full_name)
''', {})


class MNCHWApp(AppBase):
    keyword = u'mnchw'
    subkeywords = [u'help', u'nc', u'register', u'report', u'shortage']
    min_ratio = 70

    ALLOWED_ROLE_CODES = [u'ws']

    ERROR_MESSAGES = {
        u'not_registered': _(u'Please register your number with RapidSMS before sending this report'),
        u'invalid_location': _(u'You sent an incorrect location code: %(location_code)s. You sent: %(text)s'),
        u'invalid_role': _(u'You sent an incorrect role code: %(role_code)s. You sent: %(text)s'),
        u'invalid_reason': _(u'You sent an incorrect reason: %(reason_code)s. You sent: %(text)s'),
        u'invalid_message': _(u'Your message is incorrect. Please send MNCHW HELP for help. You sent: %(text)s'),
        u'unauthorized_role': _(u'You are not allowed to send this report'),
    }

    HELP_MESSAGES = {
        None: _(u'Send MNCHW HELP NC for noncompliance help. Send MNCHW HELP REGISTER for registration help. Send MNCHW HELP REPORT for report help. Send MNCHW SHORTAGE HELP for shortage help'),
        u'nc': _(u'Send MNCHW NC location-code reason-code number-of-cases'),
        u'register': _(u'Send MNCHW REGISTER location-code role-code full-name'),
        u'report': _(u'Send MNCHW REPORT location-code commodity amount commodity amount commodity amount...'),
        u'shortage': _(u'Send MNCHW SHORTAGE location-code commodity commodity commodity...'),
    }

    RESPONSE_MESSAGES = {
        u'nc': _(u'Thank you for your MNCHW non-compliance report. Reason=%(reason)s, Cases=%(cases)d, Location=%(location)s %(location_type)s'),
        u'register': _(u'Hello %(name)s! You are now registered as %(role)s at %(location)s %(location_type)s'),
        u'already_registered': _(u'Hello %(name)s! You are already registered as a %(role)s at %(location)s %(location_type)s'),
        u'report': _(u'Thank you %(name)s. Received MNCHW report for %(location)s %(location_type)s: %(pairs)s'),
        u'shortage': _(u'Thank you for your MNCHW shortage report. Location=%(location)s %(location_type)s, commodity=%(commodity)s'),
    }

    def handle(self, message):
        text = message.text.lower().strip()

        if text.startswith(self.keyword):
            try:
                text = re.sub(self.keyword, u'', message.text, count=1).strip()
                parts = text.split(None, 1)
            except ValueError:
                self.help(message)
                return True

            if len(parts) == 0:
                self.help(message)
                return True
            elif len(parts) == 1:
                subkeyword = parts[0]
                msg_text = u''
            else:
                subkeyword, msg_text = parts

            result = process.extractOne(subkeyword, self.subkeywords, score_cutoff=self.min_ratio)
            if result is None:
                self.help(message)
                return True

            handler_name, _ = result
            handler = getattr(self, u'handle_{}'.format(handler_name))
            handler(message, msg_text)
            return True

        return False

    def handle_help(self, message, msg_text):
        text = msg_text.strip()

        if text == u'':
            message.respond(self.HELP_MESSAGES[None])
            return

        key = process.extractOne(text, self.subkeywords, score_cutoff=50)
        if key is None:
            message.respond(self.HELP_MESSAGES[None])
            return

        message.respond(self.HELP_MESSAGES[key[0]])

    def handle_nc(self, message, msg_text):
        connection, reporter = getConnectionAndReporter(message,
            self.ALLOWED_ROLE_CODES)

        text = msg_text.strip()

        if text == u'':
            message.respond(self.HELP_MESSAGES[u'nc'])
            return

        if reporter is None:
            message.respond(self.ERROR_MESSAGES[u'not_registered'])
            return

        try:
            location_code, reason_code, cases = grammar(text).noncompliance()
        except parsley.ParseError:
            message.respond(self.ERROR_MESSAGES[u'invalid_message'] % {
                u'text': message.text})
            return

        location = Location.get_by_code(location_code)
        if location is None:
            message.respond(self.ERROR_MESSAGES[u'invalid_location'] % {
                u'location_code': location_code, u'text': message.text})
            return

        if reason_code not in reason_codes:
            message.respond(self.ERROR_MESSAGES[u'invalid_reason'] % {
                u'reason_code': reason_code, u'text': message.text})

        report = NonCompliance.objects.create(
            reporter=reporter,
            location=location, reason=reason_code, cases=cases, time=now(),
            connection=connection)

        message.respond(self.RESPONSE_MESSAGES[u'nc'] % {
            u'location': location.name, u'reason': report.get_reason_display(),
            u'cases': cases, u'location_type': location.type.name})

    def handle_register(self, message, msg_text):
        connection, unused = getConnectionAndReporter(message,
            self.ALLOWED_ROLE_CODES)

        text = msg_text.strip()

        if text == u'':
            message.respond(self.HELP_MESSAGES[u'register'])
            return

        try:
            location_code, role_code, full_name = grammar(text).register()
        except parsley.ParseError:
            message.respond(self.ERROR_MESSAGES[u'invalid_message'] % {
                u'text': message.text})
            return

        location = Location.get_by_code(location_code)
        if location is None:
            message.respond(self.ERROR_MESSAGES[u'invalid_location'] % {
                u'location_code': location_code, u'text': message.text})
            return

        role = Role.get_by_code(role_code)
        if role is None or role.code.lower() not in self.ALLOWED_ROLE_CODES:
            message.respond(self.ERROR_MESSAGES[u'invalid_role'] % {
                u'role_code': role_code, u'text': message.text})
            return

        kwargs = {u'location': location, u'role': role}
        kwargs[u'alias'], kwargs[u'first_name'], kwargs[u'last_name'] = Reporter.parse_name(full_name)
        rep = Reporter(**kwargs)

        if Reporter.exists(rep, connection):
            message.respond(self.RESPONSE_MESSAGES[u'already_registered'] % {
                u'name': rep.first_name, u'role': rep.role.name,
                u'location': rep.location.name,
                u'location_type': rep.location.type.name})
            return

        rep.save()
        connection.reporters.add(rep)

        message.respond(self.RESPONSE_MESSAGES[u'register'] % {u'name': rep.first_name,
            u'role': rep.role.code, u'location': rep.location.name,
            u'location_type': rep.location.type.name})

    def handle_report(self, message, msg_text):
        connection, reporter = getConnectionAndReporter(message,
            self.ALLOWED_ROLE_CODES)
        text = msg_text.strip()

        if text == u'':
            message.respond(self.HELP_MESSAGES[u'report'])
            return

        if reporter is None:
            message.respond(self.ERROR_MESSAGES[u'not_registered'])
            return

        try:
            location_code, pairs = text.split(None, 1)
            pairs = grammar(pairs).report_list()
        except (ValueError, parsley.ParseError):
            message.respond(self.ERROR_MESSAGES[u'invalid_message'] % {
                u'text': message.text})
            return

        location = Location.get_by_code(location_code)
        if location is None:
            message.respond(self.ERROR_MESSAGES[u'invalid_location'] % {
                u'location_code': location_code, u'text': message.text})
            return

        amounts = []
        commodities = []
        for code, amount in pairs:
            result = process.extractOne(code, commodity_codes, score_cutoff=50)

            if result is None:
                continue

            comm = result[0]
            amounts.append(amount)
            commodities.append(comm.upper())

            Report.objects.create(reporter=reporter,
                time=now(), connection=connection,
                location=location, commodity=comm, immunized=amount)

        response_pairs = u', '.join(u'{}={}'.format(a, b) for a, b in zip(commodities, amounts))
        message.respond(self.RESPONSE_MESSAGES[u'report'] % {u'location': location.name,
            u'location_type': location.type.name, u'pairs': response_pairs,
            u'name': reporter.first_name})

    def handle_shortage(self, message, msg_text):
        connection, reporter = getConnectionAndReporter(message,
            self.ALLOWED_ROLE_CODES)
        text = msg_text.strip()

        if text == u'':
            message.respond(self.HELP_MESSAGES[u'shortage'])
            return

        if reporter is None:
            message.respond(self.ERROR_MESSAGES[u'not_registered'])
            return

        try:
            location_code, codes = text.split(None, 1)
            codes = grammar(codes).shortage_list()
        except (ValueError, parsley.ParseError):
            message.respond(self.ERROR_MESSAGES[u'invalid_message'] % {
                u'text': message.text})
            return

        location = Location.get_by_code(location_code)
        if location is None:
            message.respond(self.ERROR_MESSAGES[u'invalid_location'] % {
                u'location_code': location_code, u'text': message.text})
            return

        results = [process.extractOne(c, codes, score_cutoff=50) for c in codes]
        commodity = None

        for result in results:
            if result is None:
                continue

            comm = result[0]

            if commodity is None:
                commodity = comm

            Shortage.objects.create(time=now(), commodity=comm,
                reporter=reporter, location=location,
                connection=connection)

        message.respond(self.RESPONSE_MESSAGES[u'shortage'] % {u'location': location.name,
            u'location_type': location.type.name, u'commodity': commodity.upper()})

    def help(self, message):
        message.respond(self.HELP_MESSAGES[None])
