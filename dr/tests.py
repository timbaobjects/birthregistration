from datetime import datetime
from unittest import TestCase

from rapidsms.tests.harness import TestScript

from dr.app import classify_date
from dr.models import DeathReport
from locations.models import Location, LocationType
from reporters.models import Reporter, Role


class ClassifyDateTest(TestCase):
    def test_first_week_of_january(self):
        # date in the first 7 days of January, 2006
        dt = datetime(2006, 1, 5)
        result = classify_date(dt)

        # result should be set to last day of
        # previous month and year
        self.assertEqual(result.year, dt.year - 1)
        self.assertEqual(result.month, 12)
        self.assertEqual(result.day, 31)

    def test_first_week_of_other_month(self):
        # date in the first 7 days of April, 2008
        dt = datetime(2008, 4, 3)
        result = classify_date(dt)

        # result should be set to last day of
        # March of same year
        self.assertEqual(result.year, dt.year)
        self.assertEqual(result.month, dt.month - 1)
        self.assertEqual(result.day, 31)

    def test_other_week_of_any_month(self):
        # date in any other part of any month
        dt = datetime(2012, 3, 15)
        result = classify_date(dt)

        # result should be set to last day of that month
        self.assertEqual(result.year, dt.year)
        self.assertEqual(result.month, dt.month)
        self.assertEqual(result.day, 31)

        # ensure it isn't different for January
        dt = datetime(2016, 1, 18)
        result = classify_date(dt)

        # result should be set to last day of that month
        self.assertEqual(result.year, dt.year)
        self.assertEqual(result.month, dt.month)
        self.assertEqual(result.day, 31)


class DeathRegistrationTestCase(TestScript):
    def setUp(self):
        lt = LocationType.objects.create(name=u'Point')
        self.location = Location.objects.create(type=lt, name=u'The Point',
            code=u'1001001')
        self.role = Role.objects.create(name=u'Death Registrar', code=u'DR')

    def test_invalid_location_registration(self):
        self.runScript(u'''
            12345 > dr register 101 dr John Doe
            12345 < You sent an incorrect location code: 101. You sent: dr register 101 dr John Doe
        ''')

    def test_invalid_role_registration(self):
        self.runScript(u'''
            12345 > dr register 1001001 br John Doe
            12345 < You sent an incorrect role code: br. You sent: dr register 1001001 br John Doe
        ''')

    def test_registration(self):
        self.runScript(u'''
            12345 > dr register 1001001 dr John Doe
            12345 < Hello John! You are now registered as DR at The Point Point
        ''')

        rep = Reporter.objects.latest(u'pk')
        self.assertEqual(rep.first_name, u'John')
        self.assertEqual(rep.last_name, u'Doe')
        self.assertEqual(rep.location, self.location)

    def test_report(self):
        ts = classify_date(datetime.now())

        self.runScript(u'''
            12345 > dr register 1001001 dr John Doe
            12345 < Hello John! You are now registered as DR at The Point Point
            12345 > dr report 1001001 AB 1 AA 3 AD 2 AC 4
            12345 < Thank you John. Received DR report for The Point Point for {}-{}-{}
        '''.format(str(ts.day).zfill(2), str(ts.month).zfill(2), ts.year))

        report = DeathReport.objects.latest(u'pk')
        reporter = Reporter.objects.latest(u'pk')

        self.assertEqual(report.data[u'AA'], 3)
        self.assertEqual(report.data[u'AB'], 1)
        self.assertEqual(report.data[u'AC'], 4)
        self.assertEqual(report.data[u'AD'], 2)

        self.assertEqual(report.time, ts)

        self.assertEqual(report.reporter, reporter)
        self.assertEqual(report.location, reporter.location)
