from django.db.models import *

from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey


class Comment(Model):
    
    # generic foreign key fields
    content_type = ForeignKey(ContentType)
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    user = ForeignKey(User)#, related_name='comments')
    created_date = DateTimeField(auto_now_add=True)
    content = TextField()

    def __unicode__(self):
        return 'Comment by {0} on {1}'.format(self.user.username, self.created_date)
    
    
