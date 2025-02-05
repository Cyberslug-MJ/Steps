# Generated by Django 5.1.4 on 2025-01-08 03:55

import django.db.models.deletion
import django_tenants.postgresql_backend.base
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('email', models.EmailField(max_length=60, unique=True, verbose_name='email')),
                ('username', models.CharField(blank=True, max_length=60, unique=True, verbose_name='username')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='last login')),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('role', models.CharField(choices=[('Admin', 'Admin'), ('Parent', 'Parent'), ('Student', 'Student'), ('Teacher', 'Teacher')], db_index=True, max_length=7)),
                ('school_name', models.CharField(blank=True, db_index=True, max_length=200, null=True)),
                ('first_name', models.CharField(blank=True, max_length=200, verbose_name='first_name')),
                ('last_name', models.CharField(blank=True, max_length=200, verbose_name='last_name')),
                ('approved', models.BooleanField(default=False, verbose_name='approved')),
                ('verified', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'CustomUser',
                'verbose_name_plural': 'CustomUser',
            },
        ),
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schema_name', models.CharField(db_index=True, max_length=63, unique=True, validators=[django_tenants.postgresql_backend.base._check_schema_name])),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Tenant',
            },
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='SchoolProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='school', serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='school profile')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('logo', models.URLField(blank=True, default='https://my-bucket.s3.amazonaws.com/my-folder/my-image.jpg?AWSAccessKeyId=EXAMPLE&Expires=1672531199&Signature=abcdef', max_length=1000, verbose_name='logo')),
                ('current_pricing', models.CharField(choices=[('Basic', 'Basic'), ('Pro', 'Pro'), ('Enterprise', 'Enterprise')], max_length=10)),
                ('subdomain_url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='profile', serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='User Profile')),
                ('profile_picture', models.URLField(blank=True, default='https://my-bucket.s3.amazonaws.com/my-folder/my-image.jpg?AWSAccessKeyId=EXAMPLE&Expires=1672531199&Signature=abcdef', max_length=1000, verbose_name='profile picture')),
                ('firstname', models.CharField(blank=True, max_length=200)),
                ('lastname', models.CharField(blank=True, max_length=200)),
                ('email', models.EmailField(editable=False, max_length=254)),
                ('address', models.CharField(blank=True, max_length=150)),
            ],
            options={
                'verbose_name_plural': 'User Profile',
            },
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(db_index=True, max_length=253, unique=True)),
                ('is_primary', models.BooleanField(db_index=True, default=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domains', to='frontline.tenant')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
