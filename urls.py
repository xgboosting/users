from django.conf.urls import include, url
from django.contrib import admin
from users import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    #url(r'^$', views.home_page, name='home_page'),
    url(r'^sign_page/$', views.sign_page, name='sign_page'),
    url(r'^logout_page/$', views.logout_view, name='logout_view'),
    url(r'^register_page/$', views.register_page, name='register_page'),
    url(r'^activate/(?P<key>.+)$', views.activation, name='activation'),
    url(r'^new-activation-link/(?P<user_id>.+)/$',views.new_activation_link, name='new_activation_link	'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^reset_password/$', views.reset_password, name='reset_password'), 
]
