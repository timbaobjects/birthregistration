# -*- coding: utf-8 -*-
import calendar
from collections import OrderedDict
from itertools import groupby
from operator import attrgetter

from django.db import connection
from pandas import period_range



def pick(keys, dictlike):
	return {k: dictlike[k] for k in keys if k in dictlike}


def values(dictlike):
	return dictlike.values()


def generate_reporting_periods():
	cursor = connection.cursor()
	cursor.execute('SELECT MIN(date), MAX(date) FROM dr_deathreport;')
	start, end = cursor.fetchone()

	month_range = [
		d for d in period_range(start, end, freq='M').to_datetime().date]
	reporting_periods = OrderedDict()
	year_extractor = attrgetter('year')

	for year, date_list in groupby(month_range, year_extractor):
		year_info = [
			(dt.month, calendar.month_name[dt.month])
			for dt in date_list
		]
		reporting_periods[year] = year_info

	return reporting_periods
