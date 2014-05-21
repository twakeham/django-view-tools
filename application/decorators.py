from functools import wraps

from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied


class View(object):
    
    '''
        View object stores various view related information.  Usually created by @view decorator but
        there is no reason not to directly instantiate it if you like.
    '''
    
    # track instances
    _views = []
    
    def __init__(self, url, view, name=None, perm=None, **opts):
        
        super(View, self).__init__()
        
        self.url = url
        self.view = view
        self.name = name
        self.perm = perm
        self.opts = opts
                
        View._views.append(self)
                
    def get_absolute_url(self, *args, **kwargs):
        
        view = getattr(self.application, self.view)
        return reverse(view, args=args, kwargs=kwargs)
    
    abs_url = property(get_absolute_url)
        
                    
def view(url, **opts):
    
    '''
        Method decorator
        Creates View instance and attaches it to application method
         
    '''
    
    def decorator(func):
            
        view = View(url, func.__name__, **opts)
        func.view = view
        return func
        
    return decorator


def login_required(func):
    
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return func(self, request, *args, **kwargs)
        else:
            return redirect(reverse('login'))
        
    return wrapper


def permission_required(*perms):
    
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            for perm in perms:
                if not request.user.has_perm(perm):
                    raise PermissionDenied
            return func(self, request, *args, **kwargs)
        return wrapper
    
    return decorator