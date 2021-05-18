from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.fields import BooleanField

class Profile(models.Model):
    ROWSPP=(
        (25,'25'),
        (50,'50'),
        (100,'100'),
        (0,'Все имеющиеся'),
    )
    CHOICES = (
        ('USD', 'USD - Dollar'),
        ('EUR', 'EUR - Euro'),
        ('UAH', 'UAH - Hryvna'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    currency = models.CharField(max_length=30, blank=True, choices=CHOICES)
    delimiter = models.CharField(max_length=30, blank=True)
    rows_per_page = models.IntegerField("Количество строк в таблице на странице",default=25, blank=False, choices=ROWSPP)
    ved_part = BooleanField("Доступ к отчетам ВЭД",default=False)
    nal_part = BooleanField("Доступ к отчетам Внутреннего рынка",default=False)
    def __str__(self):
        return str(self.bio) + " [" + str(self.user.username) +"]"

    class Meta:
        managed = True

# https://tproger.ru/translations/extending-django-user-model/#var2
#сигналы для Profile на автоматическое создание/обновление, когда мы создаем/обновляем стандартную модель пользователя (User):
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# https://metanit.com/python/django/5.8.php



'''
Можно использовать следующий код в шаблоне:

<h2>{{ user.get_full_name }}</h2>
<ul>
  <li>Имя пользователя: {{ user.username }}</li>
  <li>Местоположение: {{ user.profile.location }}</li>
  <li>Дата рождения: {{ user.profile.birth_date }}</li>
</ul>
Или такой внутри представления:

def update_profile(request, user_id):
    user = User.objects.get(pk=user_id)
    user.profile.bio = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit...'
    user.save()
'''