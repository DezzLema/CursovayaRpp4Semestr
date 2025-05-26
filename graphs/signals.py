from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserGallery

@receiver(post_save, sender=CustomUser)
def create_user_gallery(sender, instance, created, **kwargs):
    if created:
        UserGallery.objects.get_or_create(user=instance)