# -*- coding: utf-8 -*-
import os

from django.contrib.auth.decorators import login_required
from django.http import Http404
from sendfile import sendfile

from django.conf import settings


@login_required
def serve_download(request, filename=None):
    if not filename:
        raise Http404

    download_dir = os.path.normpath(settings.SENDFILE_ROOT)
    path = os.path.normpath(os.path.join(download_dir, filename))

    if not path.startswith(download_dir):
        raise Http404

    return sendfile(request, path, attachment=True)
