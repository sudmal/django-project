# Generated by Django 3.1 on 2021-02-11 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='Title',
            field=models.CharField(max_length=50),
        ),
    ]