# pylint: disable=invalid-name, line-too-long
# Generated by Django 3.2.10 on 2021-12-08 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drf_messages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='session_key',
            field=models.CharField(blank=True, help_text='The session key where the message was submitted to.', max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='messagetag',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
