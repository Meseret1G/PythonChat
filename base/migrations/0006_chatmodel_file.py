# Generated by Django 5.1.3 on 2024-12-02 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_alter_chatmodel_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmodel',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='chat_files/'),
        ),
    ]