# Generated by Django 3.0.8 on 2020-09-04 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_auto_20200825_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Thumbnail'),
        ),
    ]
