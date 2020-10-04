from django import forms

class LoginForm(forms.Form):
    login_field = forms.CharField(widget=forms.TextInput(attrs={'class': 'fadeIn second','autofocus':'yes','placeholder': 'Логин'}),max_length=64)
    pass_field = forms.CharField(widget=forms.TextInput(attrs={'class': 'fadeIn third','id':'password','type':'password','autofocus':'yes','placeholder': 'Пароль'}),max_length=64)