# Generated by Django 4.1.5 on 2023-04-05 23:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_userphoto_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomphoto',
            name='room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.home'),
        ),
    ]
