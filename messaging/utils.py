# -*- coding: utf-8 -*-
import requests

from django.conf import settings


def send_sms_message(text, number):
    url = settings.SENDSMS_URL
    username = settings.SENDSMS_USERNAME
    password = settings.SENDSMS_PASSWORD
    shortcode = settings.SENDSMS_SHORTCODE

    params = {
        'username': username,
        'password': password,
        'shortcode': shortcode,
        'phoneNo': number,
        'message': text
    }

    response = requests.get(url, params=params)
