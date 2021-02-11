from django import forms
from .models import ArticlePages
from tinymce.widgets import TinyMCE

class ArticlePagesForm(forms.ModelForm):
    Title= forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg','autofocus':'yes','placeholder': 'Заголовок страницы'}),max_length=128)
    Text = forms.CharField(widget=TinyMCE(attrs={'cols': 160, 'rows': 500}))
    class Meta:
        model = ArticlePages