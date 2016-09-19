from __future__ import unicode_literals

from reporters.models import PersistantConnection
from .baseprefix import PrefixHandler
from ..grammars import parse_report
from ..models import BirthRegistration


class ReportHandler(PrefixHandler):
    keyword = 'report'

    def handle(self, text):
        self.preprocess()
        status = self.update_message_date(text)

        if not status:
            return True

        report_data = parse_report(self.cleaned_message)

        if not report_data:
            self.respond(PrefixHandler.error_msgs['invalid_report'].format(
                self.msg.text
            ))
            return True

        try:
            if not hasattr(self.msg, 'reporter') or not self.msg.reporter:
                self.respond(PrefixHandler.error_msgs['unauthorized_reporter'])
                return True

            if not self.msg.reporter.role.code.lower() in ['br']:
                self.respond(PrefixHandler.error_msgs['unauthorized_role'])
                return True

            location = self.msg.reporter.location

            try:
                br = BirthRegistration.objects.get(
                    connection=PersistantConnection.from_message(self.msg),
                    reporter=self.msg.reporter,
                    location=location,
                    time=self.msg.datetime
                )
            except BirthRegistration.DoesNotExist:
                br = BirthRegistration(
                    connection=PersistantConnection.from_message(self.msg),
                    reporter=self.msg.reporter,
                    location=location,
                    time=self.msg.datetime
                )

            br.girls_below1 = report_data['female'].get(1)
            br.girls_1to4 = report_data['female'].get(2)
            br.girls_5to9 = report_data['female'].get(3)
            br.girls_10to18 = report_data['female'].get(4)
            br.boys_below1 = report_data['male'].get(1)
            br.boys_1to4 = report_data['male'].get(2)
            br.boys_5to9 = report_data['male'].get(3)
            br.boys_10to18 = report_data['male'].get(4)

            br.save()

            self.respond(PrefixHandler.response_msgs['report'].format(
                location=location.name,
                date=self.msg.datetime.strftime('%d/%m/%Y'),
                g1=br.girls_below1,
                g4=br.girls_1to4,
                g9=br.girls_5to9,
                g18=br.girls_10to18,
                b1=br.boys_below1,
                b4=br.boys_1to4,
                b9=br.boys_5to9,
                b18=br.boys_10to18
            ))
        except Exception, e:
            self.debug(e)

        return True
