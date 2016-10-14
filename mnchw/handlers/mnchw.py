# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from fuzzywuzzy import process
import parsley

from handlers.fuzzy import FuzzySubKeywordHandler
from locations.models import Location
from mnchw.models import NonCompliance, Report, Shortage
from reporters.models import PersistantConnection, Reporter, Role

commodity_codes = [choice[0] for choice in Report.IM_COMMODITIES]
reason_codes = [choice[0] for choice in NonCompliance.NC_REASONS]

grammar = parsley.makeGrammar('''
commodity_code = <letterOrDigit+>:code -> code
commodity_amt_pair = commodity_code:code ws <digit+>:amt -> (code, int(amt))
shortage_list_item = commodity_code:code ws -> code
report_list_item = commodity_amt_pair:pair ws -> pair
shortage_list = shortage_list_item+
report_list = report_list_item+
noncompliance = <digit+>:location_code ws <digit>:reason_code ws <digit+>:cases -> (location_code, reason_code, int(cases))
register = <digit+>:location_code ws <letterOrDigit+>:role_code ws <anything*>:full_name -> (location_code, role_code, full_name)
report = <digit+>:location_code ws <report_list>:pairs -> (location_code, pairs)
shortage = <digit+>:location_code ws <shortage_list>:items -> (location_code, items)
''', {})

ERROR_MESSAGES = {
    u'not_registered': _(u'Please register your number with RapidSMS before sending this report'),
    u'invalid_location': _(u''),
    u'invalid_role': _(u''),
    u'invalid_reason': _(u''),
    u'unknown_commodities': _(u''),
}

HELP_MESSAGES = {
    None: _(u'Send MNCHW HELP NC for noncompliance help. Send MNCHW HELP REGISTER for registration help. Send MNCHW HELP REPORT for report help. Send MNCHW SHORTAGE HELP for shortage help'),
    u'nc': _(u'Send MNCHW NC location-code reason-code number-of-cases'),
    u'register': _(u'Send MNCHW REGISTER location-code role-code full-name'),
    u'report': _(u'Send MNCHW REPORT location-code commodity amount commodity amount commodity amount...'),
    u'shortage': _(u'Send MNCHW SHORTAGE location-code commodity commodity commodity...'),
}

RESPONSE_MESSAGES = {
    u'nc': _(u''),
    u'register': _(u''),
    u'already_registered': _(u''),
    u'report': _(u''),
    u'shortage': _(u''),
}


class MNCHWHandler(FuzzySubKeywordHandler):
    '''Processes messages for the MNCHW app'''
    keyword = u'mnchw'
    subkeywords = [u'help', u'nc', u'register', u'report', u'shortage']

    def handle(self, text):
        # save connection
        connection = PersistantConnection.from_message(self.msg)
        self.persistent_connection = connection

        # mark connection as seen
        connection.seen()

        super(MNCHWHandler, self).handle(text)

    def handle_help(self, text):
        text = text.strip()

        if text == u'':
            self.respond(HELP_MESSAGES[None])
            return

        key = process.extractOne(text, self.subkeywords, score_cutoff=50)
        if key is None:
            self.respond(HELP_MESSAGES[None])
            return

        self.respond(HELP_MESSAGES[key])

    def handle_nc(self, text):
        pass

    def handle_register(self, text):
        pass

    def handle_report(self, text):
        pass

    def handle_shortage(self, text):
        pass

    def help(self):
        self.respond(HELP_MESSAGES[None])
