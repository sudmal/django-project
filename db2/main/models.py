from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    currency = models.CharField(max_length=30, blank=True)
    lastlogin = models.DateField(blank=True, null=True )


# https://tproger.ru/translations/extending-django-user-model/#var2
#сигналы для Profile на автоматическое создание/обновление, когда мы создаем/обновляем стандартную модель пользователя (User):
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()