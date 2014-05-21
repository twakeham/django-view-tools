from django.forms import *


class CommentForm(Form):
    
    comment = CharField(required=True, widget=Textarea())