from django.contrib.contenttypes.generic import GenericStackedInline
from django.contrib.admin import ModelAdmin, site

from models import Comment


site.register(Comment, ModelAdmin)


class CommentInlineAdmin(GenericStackedInline):
    
    extra = 1
    
    fields = ['content']
    
    model = Comment
        
    def save_model(self, request, obj, form, change):
        # automatically fill the comment user field
        if not change:
            obj.user = request.user
        obj.save()