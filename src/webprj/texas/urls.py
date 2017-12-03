from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^login/$', views.log_in, name="login"),
    url(r'logout/$', views.log_out, name='logout'),
    url(r'^signup/$', views.signup, name="signup"),
    url(r'lobby$', views.lobby, name='lobby'),
    url(r'^tutorial/$', views.tutorial, name='tutorial'),
    url(r'^profile/$', views.profile, name='profile'),

    url(r'newplay/$', views.newplay, name = 'newplay'),
    url(r'update_button$', views.update_button),

    url(r'addplayer$', views.addplayer, name = 'addplayer'),
    url(r'get_position$', views.get_position, name = 'get_position'),
    url(r'getjob/(?P<pos_big>\w+)/(?P<pos_small>\w+)/(?P<pos_dealer>\w+)$', views.getjob, name = 'getjob'),
    url(r'playroom/(?P<deskname>\w+)$', views.playroom, name='playroom'),

    url(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),

    url(r'forgetpassword$', views.forgetpassword, name = 'forgetpassword'),
    url(r'reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.reset, name='reset'),
    url(r'reset$', views.resetpass, name='resetpass'),

    url(r'morechips$', views.morechips, name = 'morechips'),
    url(r'chips/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.chips, name='chips'),
]