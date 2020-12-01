# -*- coding: utf-8 -*-
from datetime import datetime, time

import django_filters
from django.utils.timezone import make_aware
from rapidsms.contrib.messagelog.models import Message

def _normalize_number(phone_number):
    if phone_number.startswith('+'):
        return phone_number
    
    if phone_number.startswith('0'):
        return '+234{num}'.format(num=phone_number[1:])
    
    if phone_number.startswith('234'):
        return '+{num}'.format(num=phone_number)


class PhoneFilter(django_filters.CharFilter):
    def filter(self, queryset, value):
        if value:
            num = _normalize_number(value)

            return queryset.filter(connection__identity=num)
        
        return queryset


class MessageDateFilter(django_filters.DateFilter):
    def filter(self, queryset, value):
        if value:
            lower = make_aware(datetime.combine(value, time.min))
            upper = make_aware(datetime.combine(value, time.max))
        
            return queryset.filter(date__gte=lower, date__lte=upper)
        
        return queryset


class MessageLogFilter(django_filters.FilterSet):
    phone = PhoneFilter()
    date = MessageDateFilter()

    class Meta:
        model = Message
        fields = ('date', 'direction',)
