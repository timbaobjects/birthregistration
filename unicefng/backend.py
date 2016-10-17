# -*- coding: utf-8 -*-
from django.http import HttpResponse
from rapidsms.backends.http.views import GenericHttpBackendView
from rapidsms.router import receive


class HttpBackendView(GenericHttpBackendView):
    params = {
        'identity_name': 'from',
        'text_name': 'text',
    }

    def form_valid(self, form):
        data = form.get_incoming_data()
        message = receive(**data)
        if hasattr(message, 'responses'):
            response_body = u' '.join([r['text'] for r in message.responses])
            return HttpResponse(response_body, content_type='text/plain; charset=utf-8')
        return HttpResponse('')

