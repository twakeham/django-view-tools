from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404
#from django.conf import settings

from forms import CommentForm
from models import Comment


class CommentReadMixin(object):
    
    '''Mixin class for use with single object views'''
    
    comment_paginator = Paginator
    comment_page_size = 25
    
    def __init__(self, **kwargs):
        
        self.comment_paginator = kwargs.pop('comment_paginator', self.comment_paginator)
        self.comment_page_size = kwargs.pop('comment_page_size', self.comment_page_size)
        
        super(CommentReadMixin, self).__init__(**kwargs)
    
    def get_context(self, request):
        context = super(CommentReadMixin, self).get_context(request)
        comments = context['object'].comments.all()
    
        paginator = self.comment_paginator(comments, self.comment_page_size)
        
        page = request.GET.get('page')
        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(self.paginator_obj.num_pages)
            
        context.update({
            'comments': comments,
            'comment_paginator': paginator 
        })        
        
        return context
    
    
class CommentCreateMixin(object):
    
    comment_form = CommentForm
    
    comment_id_format = 'comment-{0}'
    
    comment_post_save_redirect = None
    
    on_comment_save = None
        
    def __init__(self, **kwargs):
        
        self.comment_form = kwargs.pop('comment_form', self.comment_form)
        self.comment_id_format = kwargs.pop('comment_id_format', self.comment_id_format)
        self.comment_post_save_redirect = kwargs.pop('comment_post_save_redirect', self.comment_post_save_redirect)
        
        self.on_comment_save = kwargs.pop('on_comment_save', self.on_comment_save)
        
        super(CommentCreateMixin, self).__init__(**kwargs)
        
    def get_context(self, request):
        context = super(CommentCreateMixin, self).get_context(request)
        context['comment_form'] = self.comment_form()
        return context
    
    def __call__(self, request, *args, **kwargs):

        if kwargs.has_key('object_id'):
            object_id = kwargs['object_id']
            object = self.model.objects.get(pk=object_id)
        elif kwargs.has_key('slug'):
            object = self.model.objects.get(slug=kwargs['slug'])
            object_id = object.pk
        else:
            raise Http404
        
        if request.method == 'POST':
            form = self.comment_form(request.POST)
            if form.is_valid():                
                comment = Comment(
                    content_type=ContentType.objects.get_for_model(self.model),
                    object_id=object_id,
                    user=request.user,
                    content=form.cleaned_data['comment']                     
                )
                comment.save()
                
                if self.on_comment_save:
                    self.on_comment_save(comment)
                
                if self.comment_post_save_redirect:
                    url = reverse(self.comment_post_save_redirect, kwargs={'object_id': object_id})
                    anchor = self.comment_id_format.format(comment.id)
                    return redirect('{0}#{1}'.format(url, anchor))
                else:
                    return redirect(object.get_absolute_url())
                
        return super(CommentCreateMixin, self).__call__(request, *args, **kwargs)
                
                
                
