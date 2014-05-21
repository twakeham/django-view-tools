from functools import wraps

from django.core.urlresolvers import reverse
from django.conf.urls import patterns, include, url
from django.shortcuts import render, redirect

from decorators import *

# this should be somewhere else
def mix(*args):
    return type('abc', tuple(args), {})
                
                
class Application(object):  
    
    '''
        Object for grouping a number of views into a coherent single Application.
        
        Use @view decorator on methods to define views of the application
    '''
    
    notifications = []
    
    def __init__(self):
        super(Application, self).__init__()
             
        self.views = []
        for attr in dir(self):
            value = getattr(self, attr)
            if callable(value) and hasattr(value, 'view'):
                view = value.view
                view.application = self
                self.views.append(view)   
                
    def _view_map(self):
        views = []
        for view in self.views:
            views.append([self.model._meta.app_label, self.model._meta.verbose_name, view.name])
        return views         
    
    def get_urls(self):
        
        '''
            Return a list of urls for the Application.
            
            Named URLConfs are available as app.model.name  
        '''
        
        views = []
        for view in self.views:
            if view.name:
                name = "{0}.{1}.{2}".format(self.model._meta.app_label, self.model._meta.verbose_name, view.name)
                views.append(url(view.url, getattr(self, view.view), view.opts, name=name))
            else:
                views.append(url(view.url, getattr(self, view.view), view.opts))
                    
        return patterns('', *views)
    
    # for prettier urls.py
    urls = property(get_urls)
    


