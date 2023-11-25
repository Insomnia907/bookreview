from django import forms

class PostForm(forms.Form):
    title = forms.CharField(max_length=255)
    author = forms.CharField(max_length=255)
