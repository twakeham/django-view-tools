from django.core.exceptions import ImproperlyConfigured
from django.forms.models import modelform_factory
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.dispatch import Signal

from generic.views import GenericView


class GenericCreateView(GenericView):

    '''
        Generic view for creating model instances.
        
        Options -
            model - the model to create view for
            form - the form to use if model is no defined. NOTE - model or form is required
            template - template path, defaults to app_name/create.html 
            extra_context - dictionary containing extra template context, defaults to {}
            autofill_user - should the view automatically set a field to the authenticated user, defaults to False
            user_field - the field that should be automatically set to the current authenticated user
            post_save_redirect - view to go to after save.  If not defined, redirects to saved object's absolute url
            post_save_key_field - field name of key used to identify object post save, deafults to 'object_id'
            
            on_save - callback when object is saved; args - instance
            
        Template Context -
            form - created model form or form supplied by form option 
    '''        
    
    template = None
    form = None
    
    user_field = 'user'
    autofill_user = False
    
    post_save_redirect = None
    post_save_model_field = 'pk'
    post_save_key_field = 'object_id'
    
    on_save = None
    
    def __init__(self, **kwargs):
        
        self.autofill_user = kwargs.pop('autofill_user', self.autofill_user)
        self.user_field = kwargs.pop('user_field', self.user_field)
                
        self.post_save_redirect = kwargs.pop('post_save_redirect', self.post_save_redirect)
        self.post_save_model_field = kwargs.pop('post_save_model_field', self.post_save_model_field)
        self.post_save_key_field = kwargs.pop('post_save_key_field', self.post_save_key_field)
        
        self.on_save = kwargs.pop('on_save', self.on_save)
        
        super(GenericCreateView, self).__init__(**kwargs)
        
        # this needs to be done after the super call because it relies on model attribute created by superclass
        self.form = kwargs.pop('form', self.form)
        if not self.form:
            self.form = modelform_factory(self.model)
            
        self.template = kwargs.get('template', getattr(self.__class__, 'template', '{0}/create.html'.format(self.model._meta.app_label)))
        
    def get_context(self, request):
        context = super(GenericCreateView, self).get_context(request)
        context['form'] = self.form()
        return context
        
    def __call__(self, request, *args, **kwargs):
        # checks if the page has post variables from a submitted form and tries to save a model instance
        # anything failing results in being directed back to form page which can have form error msgs
        if request.method == 'POST':
            form = self.form(request.POST, request.FILES)
            if form.is_valid():
                object = form.save(commit=False)
                if self.autofill_user:
                    setattr(object, self.user_field, request.user)
                object.save()
                if self.on_save:
                    self.on_save(object)
                if self.post_save_redirect:
                    return redirect(reverse(self.post_save_redirect, kwargs={self.post_save_key_field: getattr(object, self.post_save_model_field)}))
                else:
                    return redirect(object.get_absolute_url())
            
        else:
                
            context = self.get_context(request)
            return render(request, self.template, context)
        

class GenericReadView(GenericView):
    
    '''
        Generic view for basic read of a model instance.
        
        Options -
            template - template path, defaults to app_name/read.html 
            
        Template Context -
            object - the object being read 
            
        Expects to receive either object_id or slug from URLConf
    '''
    
    template = None
       
    def __init__(self, **kwargs):
                                
        super(GenericReadView, self).__init__(**kwargs)
        
        self.template = kwargs.get('template', getattr(self.__class__, 'template', '{0}/read.html'.format(self.model._meta.app_label)))
        
    def get_context(self, request):
        context = super(GenericReadView, self).get_context(request)
        context['object'] = self.object
        return context
        
    def __call__(self, request, *args, **kwargs):
        
        if kwargs.has_key('object_id'):
            self.object = self.model.objects.get(pk=kwargs['object_id'])
        elif kwargs.has_key('slug'):
            self.object = self.model.objects.get(slug=kwargs['slug'])
        else:
            raise Http404
        
        context = self.get_context(request)
        return render(request, self.template, context)
    
    
class GenericUpdateView(GenericView):
    
    '''
        Generic view for updating model instances.
        
        Options -
            form - the form to use if model is no defined. NOTE - model or form is required
            template - template path, defaults to app_name/create.html 
            set_model_fields - a dictionary of predetermined field:value pairs to save
            post_save_redirect - view to go to after save.  If not defined, redirects to saved object's absolute url
            post_save_key_field - field name of key used to identify object post save, deafults to 'object_id'
            on_save - callback when object is saved; args - instance
            
        Template Context -
            form - created model form or form supplied by form option
            object - object being modified 
            
        Expects to receive either object_id or slug from URLConf
    '''
    
    form = None
    
    template = None
    extra_context = {}
    
    set_model_fields = {}
    
    post_save_redirect = None
    post_save_model_key = 'id'
    post_save_key_field = 'object_id'
    
    on_save = None
        
    def __init__(self, **kwargs):
                   
        self.set_model_fields = kwargs.pop('set_model_fields', self.set_model_fields)
                
        self.post_save_redirect = kwargs.pop('post_save_redirect', self.post_save_redirect)
        self.post_save_model_key = kwargs.pop('post_save_model_key', self.post_save_model_key)
        self.post_save_key_field = kwargs.pop('post_save_key_field', self.post_save_key_field)
        
        self.on_save = kwargs.pop('on_save', self.on_save)
        
        super(GenericUpdateView, self).__init__(**kwargs)
        
        # this needs to be done after the super call because it relies on model attribute created by superclass
        self.form = kwargs.pop('form', self.form)
        if not self.form:
            self.form = modelform_factory(self.model)
            
        self.template = kwargs.get('template', getattr(self.__class__, 'template', '{0}/update.html'.format(self.model._meta.app_label)))
        
    def get_context(self, request):
        
        context = super(GenericUpdateView, self).get_context(request)
        context['form'] = self.form(instance=self.object)
        context['object'] = self.object
        return context
            
    def __call__(self, request, *args, **kwargs):
    
        if kwargs.has_key('object_id'):
            self.object = self.model.objects.get(pk=kwargs['object_id'])
        elif kwargs.has_key('slug'):
            self.object = self.model.objects.get(slug=kwargs['slug'])
        else:
            raise Http404

        if request.method == 'POST':
            form = self.form(request.POST, request.FILES, instance=self.object)
            if form.is_valid():
                object = form.save(commit=False)
                for key, value in self.set_model_fields.iteritems():
                    if callable(value):
                        setattr(object, key, value(object))
                    else:
                        setattr(object, key, value)
                object.save()
                
                if self.on_save:
                    self.on_save(object)
                    
                if self.post_save_redirect:
                    return redirect(reverse(self.post_save_redirect, kwargs={self.post_save_key_field: getattr(object, self.post_save_model_key)}))
                else:
                    return redirect(object.get_absolute_url())
            
        else:  
            context = self.get_context(request)
            return render(request, self.template, context)
        
        
class GenericDeleteView(object):
    
    '''
        Generic view for deleting model instances.
        
        Options -
            post_delete_redirect - view to go to after delete.  Required.
                    
        Expects to receive either object_id or slug from URLConf
    '''
            
    post_delete_redirect = None
       
    def __init__(self, **kwargs):
        
        self.post_delete_redirect = kwargs.pop('post_delete_redirect', self.post_delete_redirect)
        if not self.post_delete_redirect:
            raise ImproperlyConfigured("'%s' must define 'post_delete_redirect'" % self.__class__.__name__)
        
        super(GenericDeleteView, self).__init__(**kwargs)
        
    def get_context(self, request):
        
        context = super(GenericDeleteView, self).get_context(request)
        context['object'] = self.object
        return context
         
    def __call__(self, request, *args, **kwargs):
        
        if kwargs.has_key('object_id'):
            self.object = self.model.objects.get(pk=kwargs['object_id'])
        elif kwargs.has_key('slug'):
            self.object = self.model.objects.get(slug=kwargs['slug'])
        else:
            raise Http404
        
        self.object.delete()
        return redirect(self.post_delete_redirect)
        
    
