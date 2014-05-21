from django.forms import Form
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class PageMixin(object):
    
    '''
        Pagination mixin for generic list views
        
        Options -
            paginator - paginator object. Should have the same interface as django.core.paginator.Paginator
            page_size - number of objects per page
            
        Template Context -
            page - paginator object for collection of page number and available pages
            
        NOTE-
            In most cases PageMixin should be the last generic list mixin applied due to its effect on the
            queryset
    '''
    
    paginator = Paginator
    page_size = 50 
            
    def __init__(self, **kwargs):
        
        self.paginator = kwargs.pop('paginator', self.paginator)
        self.page_size = kwargs.pop('page_size', self.page_size)
        
        super(PageMixin, self).__init__(**kwargs)
        
    def get_queryset(self, request):
        
        queryset = super(PageMixin, self).get_queryset(request)
        self.paginator_obj = self.paginator(queryset, self.page_size)
        
        # modify queryset to only contain objects that should be on the current page
        page = request.GET.get('page')
        try:
            queryset = self.paginator_obj.page(page)
        except PageNotAnInteger:
            queryset = self.paginator_obj.page(1)
        except EmptyPage:
            queryset = self.paginator_obj.page(self.paginator_obj.num_pages)
        
        return queryset
    
    def get_context(self, request):
        
        context = super(PageMixin, self).get_context(request)
        context['page'] = self.paginator_obj
        return context
               
        
class FilterMixin(object):
    
    '''
        Filter mixin for generic list views
        
        Options -
            filter_fields - list of fields that may be filtered
            default_filter - dictionary containing default filtering with keys as field name
                             eg. {'closed': False}
                             
        Template context -
            filter_form - auto generated form for selection filters
            
        NOTE -
            this mixin requires sessions
    '''
    
    filter_fields = []
    default_filter = {}
    
    def __init__(self, **kwargs):
        
        self.filter_fields = kwargs.pop('filter_fields', self.filter_fields)
        self.default_filter = kwargs.pop('default_filter', self.default_filter)
        
        super(FilterMixin, self).__init__(**kwargs)
        
    
    def _filter_form(self):
        
        # this function uses hidden internal django methods and may not be safe in the future
        # loops through defined filter_fields names, finds the actual db field object and gets
        # its appropriate form field
        fields = {}
        for field in self.filter_fields:
            db_field = self.model._meta.get_field_by_name(field)[0]
            fields[field] = db_field.formfield(required=False)
            
        # dynamically create a Form subclass from generated form fields                
        return type(self.__class__.__name__ + 'Form', (Form, ), fields)
    
    def get_queryset(self, request):
        
        queryset = super(FilterMixin, self).get_queryset(request)
        
        # set filter to be default_filter if nothing is already set
        if request.session.get('filter', None):
            request.session.filter = self.default_filter
        
        if request.method == 'POST':
            form = self._filter_form()(request.POST)
            if form.is_valid():
                # django forms give empty strings for missing, we need to not have them in the filter
                filters = {}
                for key, val in form.cleaned_data.iteritems():
                    # this is dangerous for boolean field filters
                    # probably need to remove False condition and use NullableBooleanField in cases
                    # where querysets need to be filtered by boolean fields
                    if val or val is False:
                        filters[key] = val
                
                request.session['filter'] = filters
                
        filters = request.session.get('filter', {})
        
        # filter queryset
        return queryset.filter(**filters)
    
    def get_context(self, request):
        context = super(FilterMixin, self).get_context(request)
        
        filters = request.session.get('filter', [])
        form = self._filter_form()(initial=filters)
        context['filter_form'] = form 
        return context
        
        
class SortMixin(object):
    
    '''
        Sort mixin for generic list views
        
        Options -
            sort_fields - list of fields that data may be sorted by
            default_sort_field - field that is sorted by default
            default_sort_order - order of default sort
                                         
        Template context -
            sort_fields - list of fields which can be sorted
            sort_field - current sort field
            sort_order - current sort direction
            
        NOTE -
            this mixin requires sessions
    '''
    
    sort_fields = []
    default_sort_field = None
    default_sort_order = 'asc'
    
    def __init__(self, **kwargs):
        
        self.sort_fields = kwargs.pop('sort_fields', self.sort_fields)
        self.default_sort_field = kwargs.pop('default_sort_field', self.default_sort_field)
        self.default_sort_order = kwargs.pop('default_sort_order', self.default_sort_order)
    
        super(SortMixin, self).__init__(**kwargs)
    
    def get_queryset(self, request):
        
        queryset = super(SortMixin, self).get_queryset(request)
        
        if request.method == 'GET':
            sort_field = request.GET.get('sort_field', None)
            if sort_field:
                request.session['sort_field'] = sort_field
                request.session['sort_order'] = request.GET.get('sort_order', 'asc')
        
        sort_field = request.session.get('sort_field', self.default_sort_field)
        if not sort_field:
            return queryset
        
        sort_order = request.session.get('sort_order', self.default_sort_order)
        
        if sort_order == 'dec':
            sort_field = '-' + sort_field
            
        return queryset.order_by(sort_field)
    
    def get_context(self, request):
        
        context = super(SortMixin, self).get_context(request)
        context['sort_fields'] = self.sort_fields 
        context['sort_field'] = request.session.get('sort_field', None)
        context['sort_order'] = request.session.get('sort_order', None)
        return context