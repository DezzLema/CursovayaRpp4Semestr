from django import forms
from .models import Graph
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class GraphForm(forms.ModelForm):
    class Meta:
        model = Graph
        fields = ['title', 'a', 'b', 'c']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'a': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'id': 'id_a'
            }),
            'b': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'id': 'id_b'
            }),
            'c': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'id': 'id_c'
            }),
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.user_type = 'registered'  # Автоматически устанавливаем статус
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)