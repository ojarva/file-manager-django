from django.contrib import admin
from django.urls import path, re_path

from files import views

urlpatterns = [
	re_path(r'^$', views.main, name="index", kwargs={"template_name": "files/index.html"}),
	re_path(r'^browse/([a-z_]+)/(.*)$', views.browse, name="browse", kwargs={"template_name": "files/browse.html"}),
	re_path(r'^upload/([a-z_]+)/(.*)$', views.upload, name="upload"),
	re_path(r'^delete/([a-z_]+)/(.+)$', views.delete, name="delete"),
	re_path(r'^permissions_save/([a-z_]+)/(.*)$', views.permissions_save, name="permissions_save"),
	re_path(r'^mkdir/([a-z_]+)/(.*)$', views.mkdir, name="mkdir"),
]
