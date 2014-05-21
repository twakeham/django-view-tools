from django.core.exceptions import ImproperlyConfigured

from application import Application, view
from application.views.single import *
from application.views.list import GenericListView

class CRUDApplication(Application):
    
    '''
        Generic application providing complete CRUD capability.
    '''
    
    name = ''
    model = None
    
    list_template = None
    create_template = None
    read_template = None
    update_template = None
    
    list_urlconf = r'^$'
    create_urlconf = r'^create/$'
    read_urlconf = r'^read/(?P<object_id>\d+)/$'
    update_urlconf = r'^update/(?P<object_id>\d+)/$'
    delete_urlconf = r'^delete/(?P<object_id>\d+)/$'
    
    list_login = False
    create_login = True
    read_login = False
    update_login = True
    delete_login = True
    
    list_perm = None
    create_perm = 'create'
    read_perm = None
    update_perm = 'update'
    delete_perm = 'delete'
        
    def __init__(self, **kwargs):
                
        self.model = kwargs.pop('model', self.model)
        if not self.model:
            raise ImproperlyConfigured("'%s' must define 'model'" % self.__class__.__name__)

        template_name = lambda action: '{0}/{1}/{2}.html'.format(self.model._meta.app_label.lower(), self.model._meta.verbose_name.lower(), action)

        self.list_template = kwargs.pop('list_template', getattr(self.__class__, 'list_template') or template_name('list'))
        self.create_template = kwargs.pop('create_template', getattr(self.__class__, 'create_template') or template_name('create'))
        self.read_template = kwargs.pop('read_template', getattr(self.__class__, 'read_template') or template_name('read'))
        self.update_template = kwargs.pop('update_template', getattr(self.__class__, 'update_template') or template_name('update'))
        self.delete_template = kwargs.pop('delete_template', getattr(self.__class__, 'delete_template') or template_name('delete'))
                
        super(CRUDApplication, self).__init__()
                
    @view(list_urlconf, login_required=list_login, perm=list_perm, name='list')
    def list(self, request, *args, **kwargs):
        return GenericListView(
            model=self.model,
            template=self.list_template
        )(request, *args, **kwargs)
        
    @view(create_urlconf, login_required=create_login, perm=create_perm, name='create')
    def create(self, request, *args, **kwargs):
        return GenericCreateView(
            model=self.model,
            template=self.create_template
        )(request, *args, **kwargs)
        
    @view(read_urlconf, login_required=read_login, perm=read_perm, name='read')
    def read(self, request, *args, **kwargs):
        return GenericReadView(
            model=self.model,
            template=self.read_template
        )(request, *args, **kwargs)
        
    @view(update_urlconf, login_required=update_login, perm=update_perm, name='update')
    def update(self, request, *args, **kwargs):
        return GenericUpdateView(
            model=self.model,
            template=self.update_template
        )(request, *args, **kwargs)
        
    @view(delete_urlconf, login_required=delete_login, perm=delete_perm, name='delete')
    def delete(self, request, *args, **kwargs):
        return GenericDeleteView(
            model=self.model,
            post_delete_redirect=self.list.view.get_absolute_url()
        )(request, *args, **kwargs)
        
 