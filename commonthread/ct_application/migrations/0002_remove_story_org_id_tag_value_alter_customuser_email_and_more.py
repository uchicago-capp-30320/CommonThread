# Generated by Django 5.2 on 2025-05-08 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ct_application', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='story',
            name='org_id',
        ),
        migrations.AddField(
            model_name='tag',
            name='value',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='name',
            field=models.CharField(max_length=50, verbose_name='display name'),
        ),
        migrations.DeleteModel(
            name='UserLogin',
        ),
    ]
