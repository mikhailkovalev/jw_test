# Generated by Django 3.1.3 on 2020-12-01 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hosting', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='postcontent',
            options={'ordering': ('position',)},
        ),
        migrations.AlterField(
            model_name='postcontent',
            name='position',
            field=models.PositiveIntegerField(default=0, verbose_name="Attachment's Position"),
        ),
    ]
