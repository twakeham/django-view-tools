from abc import ABCMeta, abstractmethod

from django.core.exceptions import ImproperlyConfigured


class GenericView(object):
    
    '''
        Abstract base generic view.
        
        Options -
            model - the model to create view for. Required 
            queryset - base queryset for list views, defaults to all objects
            extra_context - dictionary containing extra template context, defaults to {}
            
    '''
    # this is an abstract base class, so disallow direct instantiation
    __metaclass__ = ABCMeta
    
    model = None
    queryset = None
    extra_context = {}
    
    def __init__(self, **kwargs):
        
        # all generic views must define the model they operate on
        self.model = kwargs.pop('model', self.model)
        if not self.model:
            raise ImproperlyConfigured("'%s' must define model'" % self.__class__.__name__)
        
        self.extra_context = kwargs.pop('extra_context', self.extra_context)
        self.queryset = kwargs.pop('queryset', self.queryset)
        
        super(GenericView, self).__init__()
        
    def get_queryset(self, request):
        '''Return supplied queryset, or all objects for supplied model'''
        if self.queryset is None:
            return self.model.objects.all()
        return self.queryset
    
    def get_context(self, request):
        '''Return supplied extra_context'''
        return self.extra_context
    
    @abstractmethod
    def __call__(self, request, *args, **kwargs):
        '''Abstract method must be overridden.  Implement view rendering here'''        
        # instantiating a sublass without overriding __call__ will result in TypeError exception