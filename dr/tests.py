from rapidsms.tests.harness import TestScript

from dr.models import DeathReport
from locations.models import Location, LocationType
from reporters.models import Reporter, Role


class DeathRegistrationTestCase(TestScript):
    def setUp(self):
        lt = LocationType.objects.create(name=u'Point')
        self.location = Location.objects.create(type=lt, name=u'The Point',
            code=u'1001001')
        self.role = Role.objects.create(name=u'Death Registrar', code=u'DR')

    def test_registration(self):
        # invalid location code
        self.runScript(u'''
            12345 > dr register 101 dr John Doe
            12345 < You sent an incorrect location code: 101. You sent: dr register 101 dr John Doe
        ''')
        # invalid role code
        self.runScript(u'''
            12345 > dr register 1001001 br John Doe
            12345 < You sent an incorrect role code: br. You sent: dr register 1001001 br John Doe
        ''')
        # correct registration
        self.runScript(u'''
            12345 > dr register 1001001 dr John Doe
            12345 < Hello John! You are now registered as DR at The Point Point
        ''')

        rep = Reporter.objects.latest(u'pk')
        self.assertEqual(rep.first_name, u'John')
        self.assertEqual(rep.last_name, u'Doe')
        self.assertEqual(rep.location, self.location)

    def test_report(self):
        pass
