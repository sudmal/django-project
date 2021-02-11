# Generated by Django 3.1 on 2021-02-11 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Title', models.CharField(max_length=30)),
                ('Created', models.DateTimeField(auto_now=True, verbose_name='Created')),
                ('Text', models.TextField(max_length=65534)),
            ],
        ),
    ]
