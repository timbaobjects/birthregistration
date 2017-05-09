# -*- coding: utf-8 -*-
from reporters.models import PersistantConnection, Reporter


def getConnectionAndReporter(message, permitted_role_codes):
	connection = PersistantConnection.from_message(message)
	reporter = connection.reporters.filter(
		role__code__in=permitted_role_codes).order_by(u'-pk').first()

	# mark connection as seen
	connection.seen()

	return connection, reporter
