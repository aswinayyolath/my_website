from django.shortcuts import  HttpResponseRedirect
from django.contrib import messages

def my_login_required(function):
    def wrapper(request, *args, **kw):
        if 'username' not in request.session:
            messages.success(request, 'You are not authorized to view this page')
            return HttpResponseRedirect('/')
        else:
            request.session['username'] = request.session['username']
            request.user.username = request.session['username']
            return function(request, *args, **kw)
    return wrapper
