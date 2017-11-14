from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^login/$', views.log_in, name="login"),
    url(r'^signup/$', views.signup, name="signup"),
    url(r'^lobby/$', views.lobby, name='lobby'),
    url(r'^tutorial/$', views.tutorial, name='tutorial'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^playroom/$', views.playroom, name='playroom'),
    url(r'^logout/$', views.logout, name='logout'),
]
