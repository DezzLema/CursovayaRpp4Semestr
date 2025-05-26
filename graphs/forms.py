from django import forms
from .models import Graph
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class GraphForm(forms.ModelForm):
    class Meta:
        model = Graph
        fields = ['title', 'a', 'b', 'c']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        graph = super().save(commit=False)
        graph.user = self.user
        graph.gallery = self.user.gallery  # Автоматически привязываем к галерее пользователя
        if commit:
            graph.save()
        return graph

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


class AdminUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'is_active']
        widgets = {
            'user_type': forms.Select(choices=CustomUser.USER_TYPE_CHOICES),
        }


class AdminUserAddForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user
