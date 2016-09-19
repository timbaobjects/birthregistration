from __future__ import unicode_literals

from locations.models import Location
from reporters.models import PersistantConnection, Reporter, Role

from .baseprefix import PrefixHandler


class RegistrationHandler(PrefixHandler):
    keyword = 'register'

    def handle(self, text):
        self.preprocess()
        status = self.update_message_date(text)

        if not status:
            return True

        parts = self.cleaned_message.split()

        location_code = parts.pop(0)
        role_code = parts.pop(0)
        name = ' '.join(parts)

        data = {}

        try:
            data['location'] = Location.objects.get(code=location_code)
            data['role'] = Role.objects.get(code__iexact=role_code)
            data['alias'], data['first_name'], data['last_name'] = Reporter.parse_name(name)

            reporter = Reporter(**data)
            connection = PersistantConnection.from_message(self.msg)

            if Reporter.exists(reporter, connection):
                print 'Already registered'
                self.respond(PrefixHandler.response_msgs['already_registered'].format(
                    name=reporter.first_name,
                    role=reporter.role,
                    location_name=reporter.location
                ))
                return True

            reporter.save()
            connection.reporter = reporter
            connection.save()

            self.respond(PrefixHandler.response_msgs['registered'].format(
                name=reporter.first_name,
                role=reporter.role,
                location_name=reporter.location,
                location_type=reporter.location.type
            ))
            print 'New registration'
        except Location.DoesNotExist:
            self.respond(PrefixHandler.error_msgs['invalid_location'].format(location_code, self.msg.text))
        except Role.DoesNotExist:
            self.respond(PrefixHandler.error_msgs['invalid_role'].format(role_code, self.msg.text))

        return True
