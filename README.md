Django file manager
===================

This is an old project originally made for Futurice for easily sharing files with clients and between colleagues; from the era before Dropbox, Google Drive etc. were popular and widely accepted tools.

This service is built on [Django](http://djangoproject.com) 
[jQuery-File-Upload](https://github.com/blueimp/jQuery-File-Upload) and 
[Bootstrap](http://twitter.github.com/bootstrap/).

Setting up
==========

* Run grep to find references to Futurice (some static files here and there):

```
grep -R -i futurice *
```

* Install dependencies (requirements.txt)
* Configure authentication for application URL
* Start fastcgi server (*./bin/restart.sh*)
* Configure apache2 & fastcgi (or wsgi). We use following configuration:

```
RewriteEngine on
RewriteRule ^/filemanager/static/(.*)$ /home/filemanager/static/$1 [QSA,L]
FastCGIExternalServer /var/www/filemanager.fcgi -socket /home/filemanager/filemanager.sock
RewriteRule ^/filemanager/(.*)$ /filemanager.fcgi/$1 [QSA,L]
```


Assumptions in the code (feel free to change, just good to know):

* Run *python manage.py collectstatic* and *python manage.py compress* when you change static files.
* URL is */filemanager/* (mainly for static files, majority of URLs are generated automatically)
* */home/u/username/* style home folders
* *~/public_html* accessible over http
* *~/public_ssl* accessible over https
* *~/upload* not accessible over web server
* *.htaccess* enabled
* [pubtkt](https://neon1.net/mod_auth_pubtkt/install.html) configured on the server
* Write access to everyone's home folder
* Sudo access without password to */root/safe_chown.py*


Licensing
=========

See LICENSE.txt

jQuery-File-Upload
------------------

[MIT license](http://www.opensource.org/licenses/MIT)

Bootstrap
---------

[Apache license](https://github.com/twitter/bootstrap/blob/master/LICENSE)


