from django.urls import reverse
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
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "User Galleries"
        constraints = [
            models.UniqueConstraint(fields=['title'], name='unique_gallery_title')
        ]

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f"Галерея {self.user.username}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


def graph_image_path(instance, filename):
    return f'graphs/user_{instance.user.id}/{filename}'


class Graph(models.Model):
    COLOR_CHOICES = [
        ('blue', 'Синий'),
        ('red', 'Красный'),
        ('green', 'Зеленый'),
        ('black', 'Черный'),
        ('purple', 'Фиолетовый'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gallery = models.ForeignKey(UserGallery, on_delete=models.CASCADE, related_name='graphs')
    title = models.CharField(max_length=100)
    a = models.FloatField()
    b = models.FloatField()
    c = models.FloatField()
    line_color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='blue')
    line_width = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_graph_url(self):
        return reverse('generate_graph', kwargs={'graph_id': self.id})

    class Meta:
        permissions = [
            ('add_to_gallery', 'Can add graph to gallery'),
        ]

    def save(self, *args, **kwargs):
        # Генерируем изображение графика перед сохранением
        super().save(*args, **kwargs)

    def get_graph_url(self):
        return reverse('generate_graph', kwargs={'graph_id': self.id})

    def generate_graph_image(self):
        """Генерация изображения с учетом цвета и толщины линии"""
        plt.switch_backend('Agg')

        x = np.linspace(-10, 10, 400)
        y = self.a * x ** 2 + self.b * x + self.c

        plt.figure(figsize=(8, 6))
        plt.plot(x, y,
                 color=self.line_color,
                 linewidth=self.line_width)
        plt.title(f'График: y = {self.a}x² + {self.b}x + {self.c}')
        plt.grid(True)

        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        plt.close()
        return buffer.getvalue()


@receiver(post_save, sender=CustomUser)
def create_user_gallery(sender, instance, created, **kwargs):
    if created:
        UserGallery.objects.create(user=instance)
