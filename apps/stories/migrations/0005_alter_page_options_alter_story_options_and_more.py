# Generated by Django 5.2.4 on 2025-07-12 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0004_alter_page_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ['story__user', 'story', 'order'], 'verbose_name': 'Page', 'verbose_name_plural': 'Pages'},
        ),
        migrations.AlterModelOptions(
            name='story',
            options={'ordering': ['user', '-created_at'], 'verbose_name': 'Story', 'verbose_name_plural': 'Stories'},
        ),
        migrations.AddField(
            model_name='page',
            name='image_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
