from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^home/$', views.home, name="login"),
    url(r'^signup/$', views.signup, name = "signup"),
    url(r'^dashboard/$', views.dashboard, name = 'dashboard'),
    url(r'^$', views.home, name="home"),
]