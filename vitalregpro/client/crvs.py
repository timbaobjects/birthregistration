# -*- coding: utf-8 -*-
import calendar
import functools
import json
from collections import defaultdict
from datetime import datetime
from operator import itemgetter
from posixpath import join as p_join
from urlparse import urljoin, urlparse

from django.conf import settings

import requests
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware, now


def nested_dict_get(dictionary, dotted_key):
    '''
    Retrieved from: https://vinta.ws/code/dot-notation-obj-x-y-z-for-nested-objects-and-dictionaries-in-python.html
    '''
    keys = dotted_key.split('.')
    return functools.reduce(lambda d, key: d.get(key) if d else None, keys, dictionary)


def _is_valid(record):
    centre_name = nested_dict_get(record, 'user_created.registration_center.center_name')
    centre_id = nested_dict_get(record, 'user_created.registration_center.id')
    state_id = nested_dict_get(record, 'user_created.registration_center.state.id')
    lga_id = nested_dict_get(record, 'user_created.registration_center.lga.id')
    date_of_birth = record.get('date_of_birth')
    unique_id = record.get('unique_id')
    sex = record.get('sex')

    items = [
        centre_name,
        centre_id,
        state_id,
        lga_id,
        date_of_birth,
        unique_id,
        sex,
    ]

    return all(items)


class CRVSClient:
    AUTH_URL = 'https://vital.nationalpopulation.gov.ng/auth/login'
    REFRESH_URL = 'https://vital.nationalpopulation.gov.ng/auth/refresh'
    CENTRES_URL = 'https://vital.nationalpopulation.gov.ng/items/registration_center'
    LGAS_URL = 'https://vital.nationalpopulation.gov.ng/items/lgas'
    STATES_URL = 'https://vital.nationalpopulation.gov.ng/items/state'
    RECORDS_URL = 'https://vital.nationalpopulation.gov.ng/items/live_birth'
    LOGOUT_URL = 'https://vital.nationalpopulation.gov.ng/auth/logout'

    def authenticate(self, **credentials):
        default_credentials = {
            'email': settings.VRP_USER_ID,
            'password': settings.VRP_PASSWORD
        }
        new_credentials = default_credentials.copy()
        new_credentials.update(**credentials)

        response = requests.post(self.AUTH_URL, json=new_credentials)
        if response.status_code == 200:
            self.access_token = response.json().get('data').get('access_token')
            self.refresh_token = response.json().get('data').get('refresh_token')
            return True
        else:
            return False

    def refresh(self):
        refresh_token = getattr(self, 'refresh_token', None)

        if refresh_token is None:
            raise ValueError('Please authenticate first!')

        response = requests.post(self.REFRESH_URL, json={'refresh_token': refresh_token})
        if response.status_code == 200:
            self.access_token = response.json().get('data').get('access_token')
            self.refresh_token = response.json().get('data').get('refresh_token')
            return True
        else:
            return False

    def logout(self):
        access_token = getattr(self, 'access_token', None)
        if access_token is None:
            raise ValueError('Please authenticate first!')
        refresh_token = getattr(self, 'refresh_token', None)
        if refresh_token is None:
            raise ValueError('Please authenticate first!')

        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        body = {'refresh_token': refresh_token}
        response = requests.post(self.LOGOUT_URL, headers=headers, json=body)
        self.access_token = None
        self.refresh_token = None

    def _make_paginated_request(self, request_url, params=None):
        access_token = getattr(self, 'access_token', None)
        if access_token is None:
            raise ValueError('Please authenticate first!')

        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        if params is None:
            params = {}
        params.update(meta='filter_count', page=1)

        response = requests.get(request_url, headers=headers, params=params)
        dataset = []
        if response.status_code == 200:
            payload = response.json()
            dataset.extend(payload.get('data'))
            num_records = payload.get('meta').get('filter_count')

            while len(dataset) < num_records:
                params.update(page=params['page'] + 1)
                response = requests.get(request_url, headers=headers, params=params)
                payload = response.json()
                dataset.extend(payload.get('data'))

            return dataset

        raise Exception('Operation failed and returned: {}'.format(response.text))

    def _get_raw_births(self, registration_date):
        params = {
            'sort': 'sort,-date_created',
            'filter[status][_eq]': 2,
            'filter[date_created][_contains]': registration_date,
            'fields[]': [
                'user_created.registration_center.center_name',
                'user_created.registration_center.id',
                'user_created.registration_center.lga.id',
                'user_created.registration_center.state.id',
                'date_of_birth',
                'date_created',
                'unique_id',
                'sex'
            ],
            'page': 1,
        }

        return self._make_paginated_request(self.RECORDS_URL, params)

    def get_births(self, registration_date):
        dataset = self._get_raw_births(registration_date)

        return [self._transform_record(r) for r in dataset if _is_valid(r)]

    def get_centres(self):
        return self._make_paginated_request(self.CENTRES_URL)

    def get_centre(self, centre_code):
        access_token = getattr(self, 'access_token', None)
        if access_token is None:
            raise ValueError('Please authenticate first!')

        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        parse_result = urlparse(self.CENTRES_URL)
        request_url = urljoin(self.CENTRES_URL, p_join(parse_result.path, str(centre_code)))
        response = requests.get(request_url, headers=headers)
        if response.status_code == 200:
            return response.json()

        raise Exception('Operation failed and returned: {}'.format(response.text))

    def get_states(self):
        access_token = getattr(self, 'access_token', None)
        if access_token is None:
            raise ValueError('Please authenticate first!')

        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        response = requests.get(self.STATES_URL, headers=headers)
        if response.status_code == 200:
            return response.json().get('data')

        raise Exception('Operation failed and returned: {}'.format(response.text))

    def get_lgas(self):
        return self._make_paginated_request(self.LGAS_URL)

    def _get_age_band(self, age):
        if age.years < 1:
            return 'U1'
        elif 1 <= age.years and age.years < 5:
            return '1-4'
        elif 5 <= age.years and age.years < 10:
            return '5-9'
        elif 10 <= age.years and age.years < 18:
            return '10+'

        return None

    def _classify_date(self, record_date):
        # before or on the 15th, return the 15th
        if record_date.day <= 15:
            return make_aware(
                datetime(record_date.year, record_date.month, 15))
        # return the last day of the month for others
        else:
            month_last_day = calendar.monthrange(record_date.year,
                record_date.month)[1]
            return make_aware(
                datetime(record_date.year, record_date.month, month_last_day))

    def _transform_record(self, birth_record):
        current_timestamp = now()
        date_created = parse(birth_record.get('date_created'))
        date_of_birth = make_aware(parse(birth_record.get('date_of_birth')))
        age = relativedelta(current_timestamp, date_of_birth)
        sex = birth_record.get('sex')
        centre_id = birth_record.get('user_created').get('registration_center').get('id')
        lga_id = birth_record.get('user_created').get('registration_center').get('lga').get('id')
        state_id = birth_record.get('user_created').get('registration_center').get('state').get('id')
        centre_name = birth_record.get('user_created').get('registration_center').get('center_name')
        unique_id = birth_record.get('unique_id')

        return {
            'age_band': self._get_age_band(age),
            'sex': sex,
            'centre_name': centre_name,
            'centre_id': centre_id,
            'lga_id': lga_id,
            'state_id': state_id,
            'unique_id': unique_id,
            'report_date': date_created,
        }

    def collate_records(self, records):
        def _factory():
            return {
                'Female': {
                    'U1': 0,
                    '1-4': 0,
                    '5-9': 0,
                    '10+': 0,
                },
                'Male': {
                    'U1': 0,
                    '1-4': 0,
                    '5-9': 0,
                    '10+': 0,
                },
                'meta': {},
                'record_ids': set()
            }

        dataset = defaultdict(_factory)

        for record in records:
            centre_id = record.get('centre_id')
            centre_name = record.get('centre_name')
            lga_id = record.get('lga_id')
            state_id = record.get('state_id')
            if not centre_id or not centre_name or not lga_id or not state_id:
                continue
            if record.get('age_band') is None:
                continue
            centre_data = dataset[centre_id]
            centre_data['record_ids'].add(record.get('unique_id'))
            if len(centre_data['meta']) == 0:
                centre_data['meta']['name'] = centre_name
                centre_data['meta']['lga'] = lga_id
                centre_data['meta']['state'] = state_id
            centre_data[record.get('sex')][record.get('age_band')] += 1

        return (dataset, record.get('report_date'))
