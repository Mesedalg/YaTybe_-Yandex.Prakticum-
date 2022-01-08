from django import forms
from .models import Group


class PostForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all(),required=False)
    text = forms.CharField(widget=forms.Textarea)
