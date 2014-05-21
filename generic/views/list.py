from django.shortcuts import render

from generic.views import GenericView


class GenericListView(GenericView):
    
    template = None
    
    def __init__(self, **kwargs):
            
        super(GenericListView, self).__init__(**kwargs)
        
        self.template = kwargs.get('template', getattr(self.__class__, 'template', '{0}/read.html'.format(self.model._meta.app_label)))
        
    def get_context(self, request):
        
        context = super(GenericListView, self).get_context(request)
        context['object_list'] = self.get_queryset(request)
        return context
        
    def __call__(self, request, *args, **kwargs):
        
        context = self.get_context(request)
        return render(request, self.template, context)
    
    
