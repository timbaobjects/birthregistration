# -*- coding: utf-8 -*-
from rest_framework.authentication import TokenAuthentication


class BearerAuthentication(TokenAuthentication):
    keyword = 'Bearer'
