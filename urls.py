from django.conf.urls.defaults import *

urlpatterns = patterns('',
	url(r'^$', 'files.views.main', name="index", kwargs={"template_name": "files/index.html"}),
	url(r'^browse/([a-z_]+)/(.*)$', 'files.views.browse', name="browse", kwargs={"template_name": "files/browse.html"}),
	url(r'^upload/([a-z_]+)/(.*)$', 'files.views.upload', name="upload"),
	url(r'^delete/([a-z_]+)/(.+)$', 'files.views.delete', name="delete"),
	url(r'^permissions_save/([a-z_]+)/(.*)$', 'files.views.permissions_save', name="permissions_save"),
	url(r'^mkdir/([a-z_]+)/(.*)$', 'files.views.mkdir', name="mkdir"),
)
