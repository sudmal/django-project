from django import forms

class SearchForm(forms.Form):
    search_string = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите текст'}), max_length=100)