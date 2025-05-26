from django.db import models
from django.conf import settings
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('registered', 'Registered'),
        ('guest', 'Guest'),
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='registered'  # Установите registered по умолчанию
    )
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class UserGallery(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gallery')
    title = models.CharField(max_length=100, blank=True)  # Убрали default
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.title:  # Если название не указано
            self.title = f"Галерея {self.user.username}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


def graph_image_path(instance, filename):
    return f'graphs/user_{instance.user.id}/{filename}'


class Graph(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gallery = models.ForeignKey(UserGallery, on_delete=models.CASCADE, related_name='graphs')
    title = models.CharField(max_length=100)
    a = models.FloatField()
    b = models.FloatField()
    c = models.FloatField()
    graph_image = models.ImageField(upload_to='graphs/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ('add_to_gallery', 'Can add graph to gallery'),
        ]

    def save(self, *args, **kwargs):
        # Генерируем изображение графика перед сохранением
        self.generate_graph()
        super().save(*args, **kwargs)

    def generate_graph(self):
        plt.switch_backend('Agg')  # Для работы без GUI

        x = np.linspace(-10, 10, 400)
        y = self.a * x ** 2 + self.b * x + self.c

        plt.figure(figsize=(8, 6))
        plt.plot(x, y)
        plt.title(f'График функции: y = {self.a}x^2 + {self.b}x + {self.c}')  # Заменили ² на ^2
        plt.xlabel('x')
        plt.ylabel('y')
        plt.grid(True)

        # Сохраняем изображение во временный буфер
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        plt.close()

        # Сохраняем изображение в поле graph_image
        filename = f'graph_{self.title}_{self.id}.png'
        self.graph_image.save(filename, ContentFile(buffer.getvalue()), save=False)


@receiver(post_save, sender=CustomUser)
def create_user_gallery(sender, instance, created, **kwargs):
    if created:
        UserGallery.objects.create(user=instance)
