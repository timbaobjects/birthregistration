# -*- coding: utf-8 -*-
import logging

from django.utils.deprecation import MiddlewareMixin

from subdomains.middleware import SubdomainURLRoutingMiddleware

logger = logging.getLogger(__name__)


class SubdomainMiddleware(MiddlewareMixin, SubdomainURLRoutingMiddleware):
    pass
