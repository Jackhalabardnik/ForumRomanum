# Generated by Django 3.0.8 on 2020-08-10 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0005_auto_20200810_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
