import json
import os
import subprocess

from django.contrib.auth import get_backends
from django.contrib.auth.models import User
from django.http import (Http404, HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden, HttpResponseNotFound)
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext, loader
from django.urls import reverse
from django.views.decorators.csrf import (csrf_exempt, ensure_csrf_cookie,
                                          requires_csrf_token)
from django.views.decorators.http import condition, require_GET, require_POST

from .utils import FileOperations


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
    data = FileOperations.save_permissions(request.user.username, folder, path, settings)

    return JSONResponse(data, {}, response_mimetype(request))


@ensure_csrf_cookie
@require_GET
def main(request, template_name):
    ret_dict = {"homefolder_exists": True}
    if not FileOperations.valid_file(request.user.username, "public_html", ""):
        ret_dict["homefolder_exists"] = False
    return render(request, template_name, context=ret_dict)
    
@ensure_csrf_cookie
@require_GET
def browse(request, folder, path, template_name):
    if not FileOperations.valid_file(request.user.username, folder, path):
        raise Http404
    path = path.replace("//", "/")
    path_parts = []
    path_parts_temp = path.split("/")
    path_construct = ""
    for item in path_parts_temp[:-1]:
        path_construct = "%s/%s" % (path_construct, item)
        path_parts.append((path_construct, item))

    ret_dict = {"folder": folder, "path": path, "path_parts": path_parts, "current_path": path_parts_temp[-1] }
    return render(request, template_name, context=ret_dict)

@ensure_csrf_cookie
@requires_csrf_token
def upload(request, folder, path):
    data = []
    def get_return_dict(file):
        return {"name": file.get("filename"), "size": file.get("size"), 'url': url, "mtime": file.get("mtime", 0), "mtime_readable": file.get("mtime_readable", "-"), 'delete_url': reverse("delete", args=[folder, path+"/"+file.get("filename")]), "delete_type": "POST"}

    if request.FILES:
        files = request.FILES.get("files[]")
    else:
        files = FileOperations.get_files(request.user.username, folder, path)
        for file in files:
             if os.path.isdir(file.get("full_path")):
                 url = reverse("browse", args=[folder, path+"/"+ file.get("filename")])
             else:
                 if folder == "public_html":
                     url = "http://public.futurice.com/~%s/%s/%s" % (request.user.username, path, file.get("filename"))
                 else:
                     url = "/~%s/%s/%s" % (request.user.username, path, file.get("filename"))
             data.append(get_return_dict(file))
        return JSONResponse(data, {}, response_mimetype(request))
    f = files
    FileOperations.upload_file(f, request.user.username, folder, path)

    file = FileOperations.get_file(request.user.username, folder, path, f.name)
    if os.path.isdir(file.get("full_path")):
        url = reverse("browse", args=[folder, path+"/"+ file.get("filename")])
    else:
        if folder == "public_html":
            url = "http://public.futurice.com/~%s/%s/%s" % (request.user.username, path, file.get("filename"))
        else:
            url = f"/~{request.user.username}/{path}/{file.get('filename')}"
    data.append(get_return_dict(file))
    response = JSONResponse(data, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response

@require_POST
@ensure_csrf_cookie
@requires_csrf_token
def delete(request, folder, path):
    return JSONResponse(FileOperations.delete_file(request.user.username, folder, path), {}, response_mimetype(request))

@require_POST
@ensure_csrf_cookie
@requires_csrf_token
def mkdir(request, folder, path):
    pathname = request.POST.get("pathname")
    if not pathname:
        return HttpResponseBadRequest("Missing pathname")

    data = FileOperations.mkdir(request.user.username, folder, path, pathname)
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
