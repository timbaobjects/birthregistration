from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from unicefng.backend import HttpBackendView


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    # RapidSMS core URLs
    url(r'^accounts/', include('rapidsms.urls.login_logout')),
    # RapidSMS contrib app URLs
    url(r'^httptester/', include('rapidsms.contrib.httptester.urls')),
    url(r'^messagelog/', include('rapidsms.contrib.messagelog.urls')),
    url(r'^messaging/', include('rapidsms.contrib.messaging.urls')),
    url(r'^registration/', include('rapidsms.contrib.registration.urls')),

    # Third party URLs
    url(r'^selectable/', include('selectable.urls')),
    url(r'^br/', include('br.urls')),
    url(r'^dr/', include('dr.urls')),
    url(r'^api/', include('api.urls', namespace=u'api')),
    url(r'incoming/', HttpBackendView.as_view(backend_name='polling')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
