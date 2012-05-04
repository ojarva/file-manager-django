Django file manager
===================

We have few servers for sharing files easily. One is called 
public.futurice.com, which is accessible from everywhere.

Earlier, sftp was the only way to upload files, which is a little bit 
cumbersome. Server usage is rather versatile: some content is for 
customers, some for colleagues, and some for everyone.

To make sharing and configuring permissions easier, we made small Django 
application for managing files and folder access rules.

This service is built on [Django](http://djangoproject.com) 
[jQuery-File-Upload](https://github.com/blueimp/jQuery-File-Upload) and 
[Bootstrap](http://twitter.github.com/bootstrap/).

Setting up
==========

* Install latest Django (1.4), django_compressor and yui-compressor
* Configure authentication for application URL
* Start fastcgi server (*bin/restart.sh*)
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

Code provided by Futurice
-------------------------

Copyright (C) 2012 Futurice Ltd, Olli Jarva

Permission is hereby granted, free of charge, to any person obtaining a 
copy of this software and associated documentation files (the 
"Software"), to deal in the Software without restriction, including 
without limitation the rights to use, copy, modify, merge, publish, 
distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to 
the following conditions:

The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

jQuery-File-Upload
------------------

[MIT license](http://www.opensource.org/licenses/MIT)

Bootstrap
---------

[Apache license](https://github.com/twitter/bootstrap/blob/master/LICENSE)


