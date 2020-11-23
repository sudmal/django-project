from django import forms

class LoginForm(forms.Form):
    login_field = forms.CharField(widget=forms.TextInput(attrs={'class': 'fadeIn second','autofocus':'yes','placeholder': 'Логин'}),max_length=64)
    pass_field = forms.CharField(widget=forms.TextInput(attrs={'class': 'fadeIn third','id':'password','type':'password','autofocus':'yes','placeholder': 'Пароль'}),max_length=64)

class ProfileForm(forms.Form):
    bio = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg','autofocus':'yes','placeholder': 'Фамилия Имя Отчество'}),max_length=128)
    CHOICES= (('USD', 'USD'),('EUR', 'EUR'),('UAH', 'UAH'),)
    currency = forms.CharField(widget=forms.Select(choices=CHOICES))