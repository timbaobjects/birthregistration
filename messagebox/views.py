# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from rapidsms.contrib.messagelog.models import Message

from django.conf import settings

from .filters import MessageLogFilter


class MessageListView(LoginRequiredMixin, ListView):
    context_object_name = 'messages'
    page_title = 'Messages'
    paginate_by = settings.PAGE_SIZE
    template_name = 'messages/message_list.html'

    def get(self, request, *args, **kwargs):
        queryset = Message.objects.order_by('-date')
        self.filter_set = MessageLogFilter(request.GET, queryset=queryset)

        return super(MessageListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MessageListView, self).get_context_data(**kwargs)
        context['filter_form'] = self.filter_set.form
        context['page_title'] = self.page_title
        return context
    
    def get_queryset(self):
        return self.filter_set.qs
    