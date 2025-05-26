from django import forms
from .models import Graph, UserGallery
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.core.exceptions import ValidationError


class GraphForm(forms.ModelForm):
    class Meta:
        model = Graph
        fields = ['title', 'a', 'b', 'c', 'line_color', 'line_width']
        widgets = {
            'line_width': forms.NumberInput(attrs={
                'min': 0.1,
                'max': 10,
                'step': 0.1
            }),
            'line_color': forms.Select(attrs={
                'class': 'color-picker'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.target_user = kwargs.pop('target_user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        graph = super().save(commit=False)
        graph.user = self.user
        # Используем галерею целевого пользователя, если указан, иначе галерею текущего пользователя
        target_gallery_user = self.target_user if self.target_user else self.user
        graph.gallery = target_gallery_user.gallery
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


class GalleryEditForm(forms.ModelForm):
    class Meta:
        model = UserGallery
        fields = ['title', 'description']

    def __init__(self, *args, **kwargs):
        self.target_user = kwargs.pop('target_user', None)
        super().__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data['title']
        if UserGallery.objects.filter(title=title).exclude(id=self.instance.id).exists():
            raise ValidationError("Галерея с таким названием уже существует")
        return title
