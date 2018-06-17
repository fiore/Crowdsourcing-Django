from django.contrib.auth.models import User

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class UserForm(forms.ModelForm):
	first_name = forms.CharField(label='first_name',
		widget=forms.TextInput(attrs={'class': 'form-control', 'id' : 'first_name', 'placeholder' : 'First name'}))

	last_name = forms.CharField(label='last_name',
		widget=forms.TextInput(attrs={'class': 'form-control', 'id' : 'last_name', 'placeholder' : 'Last name'}))

	username =  forms.CharField(label='username',
		widget=forms.TextInput(attrs={'class': 'form-control', 'id' : 'username', 'placeholder' : 'Username'}))
	
	password =  forms.CharField(label='password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'id' : 'password', 'placeholder' : 'Password'}))
	
	email =  forms.CharField(label='email',
		widget=forms.EmailInput(attrs={'class': 'form-control', 'id' : 'email', 'placeholder' : 'Email'}))

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'password', 'email')

class LoginForm(forms.ModelForm):

	class Meta:
		model = User
		fields = ('username', 'password')

class UploadFileForm(forms.Form):
	file = forms.FileField()