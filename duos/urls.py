from django.conf.urls import url,handler404,handler403
from . import views

app_name = 'duos'

urlpatterns = [
    url(r'^api-(?P<api_hostname>[a-zA-Z1-9]+)/frame/auth/$',views.auth_pre,name='pre_auth'),
    url(r'^api-(?P<api_hostname>[a-zA-Z1-9]+)/frame/enroll/$',views.enroll,name='enroll'),
    url(r'^api-(?P<api_hostname>[a-zA-Z1-9]+)/frame/auth_check_ws/$',views.auth_check_ws,name='auth_check_ws'),
    url(r'^api-(?P<api_hostname>[a-zA-Z1-9]+)/frame/auth_/$',views.auth,name='auth'),
]



