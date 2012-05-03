from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_backends
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST

from models import get_file, get_files, delete_file, upload_file, mkdir_file, save_permissions

import os
import json
import subprocess
from django.views.decorators.csrf import requires_csrf_token, ensure_csrf_cookie


@requires_csrf_token
@require_POST
def permissions_save(request, folder, path):
    settings = {}
    method = request.POST.get("permission_scheme")
    if not method:
        return HttpResponseBadRequest("Missing method "+json.dumps(request.POST))
    if method == "Public":
        settings["mode"] = "public"
    if method == "Futurice SSO":
        settings["mode"] = "sso"
    if method == "Static account":
        settings["mode"] = "basicauth"
        if not request.POST.get("password") or not request.POST.get("username"):
            return HttpResponseBadRequest("Missing username or password")
        settings["username"] = request.POST.get("username")
        settings["password"] = request.POST.get("password")
    data = save_permissions(request.user.username, folder, path, settings)

    return JSONResponse(data, {}, response_mimetype(request))


@ensure_csrf_cookie
def main(request, template_name):
    ret_dict = {}
    return render_to_response(template_name, ret_dict, context_instance=RequestContext(request))

@ensure_csrf_cookie
def browse(request, folder, path, template_name):
    path = path.replace("//", "/")
    path_parts = []
    path_parts_temp = path.split("/")
    path_construct = ""
    for item in path_parts_temp[:-1]:
        path_construct = "%s/%s" % (path_construct, item)
        path_parts.append((path_construct, item))

    ret_dict = {"folder": folder, "path": path, "path_parts": path_parts, "current_path": path_parts_temp[-1] }
    return render_to_response(template_name, ret_dict, context_instance=RequestContext(request))

@ensure_csrf_cookie
@csrf_exempt
def upload(request, folder, path):
    ret_list = []
    data = []
    if request.FILES:
        files = request.FILES.get("files[]")
    else:
        files = get_files(request.user.username, folder, path)
        for file in files:
             if os.path.isdir(file.get("full_path")):
                 url = reverse("browse", args=[folder, path+"/"+ file.get("filename")])
             else:
                 url = "/~%s/%s/%s" % (request.user.username, path, file.get("filename"))
             data.append({"name": file.get("filename"), "size": file.get("size"), 'url': url, "mtime": file.get("mtime", 0), "mtime_readable": file.get("mtime_readable", "-"), 'delete_url': reverse("delete", args=[folder, path+"/"+file.get("filename")]), "delete_type": "POST"})
        return JSONResponse(data, {}, response_mimetype(request))
    f = files
    upload_file(f, request.user.username, folder, path)

    file = get_file(request.user.username, folder, path, f.name)
    if os.path.isdir(file.get("full_path")):
        url = reverse("browse", args=[folder, path+"/"+ file.get("filename")])
    else:
        url = "/~%s/%s/%s" % (request.user.username, path, file.get("filename"))
    data.append({"name": file.get("filename"), "size": file.get("size"), 'url': url, "mtime": file.get("mtime", 0), "mtime_readable": file.get("mtime_readable", "-"), 'delete_url': reverse("delete", args=[folder, path+"/"+file.get("filename")]), "delete_type": "POST"})
    response = JSONResponse(data, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response

@require_POST
@ensure_csrf_cookie
@requires_csrf_token
def delete(request, folder, path):
    return JSONResponse(delete_file(request.user.username, folder, path), {}, response_mimetype(request))

@ensure_csrf_cookie
@require_POST
@requires_csrf_token
def mkdir(request, folder, path):
    pathname = request.POST.get("pathname")
    if not pathname:
        return HttpResponseBadRequest("Missing pathname")

    data = mkdir_file(request.user.username, folder, path, pathname)
    if data.get("success"):
        data["redirect"] = reverse("browse", args=[folder, path+"/"+pathname])
    return JSONResponse(data, {}, response_mimetype(request))

class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self,obj='',json_opts={},mimetype="application/json",*args,**kwargs):
        content = json.dumps(obj,**json_opts)
        super(JSONResponse,self).__init__(content,mimetype,*args,**kwargs)

def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"
