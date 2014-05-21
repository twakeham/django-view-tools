
class FilterByUser(object):
    '''
        Queryset filter mixin restricts queryset to those records matching the authenticated user
        
        Options -
            user_field - the field which to filter by, defaults to `user`
    '''
    
    user_field = 'user'
    
    def __init__(self, **kwargs):
        self.user_field = kwargs.pop('user_field', self.user_field)
        
        super(FilterByUser, self).__init__(**kwargs)
    
    def get_queryset(self, request):
        
        queryset = super(FilterByUser, self).get_queryset(request)
        return queryset.filter()