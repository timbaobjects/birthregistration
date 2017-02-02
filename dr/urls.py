# vim: ai ts=4 sts=4 et sw=4
from django.conf.urls import url
from dr import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'reports/(?P<pk>\d+)/?$', views.DeathReportUpdateView.as_view(),
    	name=u'report_edit'),
]
