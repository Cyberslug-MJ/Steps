# Generated by Django 5.1.4 on 2024-12-24 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontline', '0004_alter_userprofile_firstname_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='first_name'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='last_name'),
        ),
    ]