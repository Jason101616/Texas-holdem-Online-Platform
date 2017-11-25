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

    url(r'newplay/(?P<room_id>\w+)', views.newplay, name = 'newplay'),

    url(r'addplayer', views.addplayer, name = 'addplayer'),
    url(r'get_position', views.get_position, name = 'get_position'),
    url(r'getjob/(?P<pos_big>\w+)/(?P<pos_small>\w+)/(?P<pos_dealer>\w+)', views.getjob, name = 'getjob'),
    url(r'playroom/(?P<deskname>\w+)$', views.playroom, name='playroom'),
]