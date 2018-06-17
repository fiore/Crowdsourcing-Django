from django.conf.urls import url
from . import views # . = current directory

app_name = 'crowdsourcing'

urlpatterns = [
		url(r'^$', views.IndexView.as_view(), name='index'),

		url(r'caratteristiche/$', views.CaratteristicheView.as_view(), name='Caratteristiche'),

		url(r'funzionamento/$', views.FunzionamentoView.as_view(), name='Funzionamento'),

		url(r'promote/$', views.Promote.as_view(), name='Promote'),

		url(r'register/$', views.Register.as_view(), name='Register'),

		url(r'login/$', views.Login.as_view(), name='Login'),

		url(r'logout/$', views.Logout, name='Logout'),

		url(r'campaign/$', views.Campaign.as_view(), name='Campaign'),

		url(r'SignUpToCampaign/(?P<campaign_id>[0-9]+)$', views.SignUpToCampaign.as_view(), name='SignUpToCampaign'),

		url(r'task/$', views.Task.as_view(), name='Task'),

		url(r'user/$', views.User.as_view(), name='User'),
]