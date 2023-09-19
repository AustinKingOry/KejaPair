# Generated by Django 4.1.5 on 2023-04-16 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_notification_trigger_user_alter_notification_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-created']},
        ),
        migrations.AddField(
            model_name='user',
            name='matches',
            field=models.ManyToManyField(blank=True, related_name='matches', to='base.match'),
        ),
        migrations.AddField(
            model_name='user',
            name='pairs',
            field=models.ManyToManyField(blank=True, related_name='pairs', to='base.pairrequest'),
        ),
    ]
