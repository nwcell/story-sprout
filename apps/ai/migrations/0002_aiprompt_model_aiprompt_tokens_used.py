# Generated by Django 5.2.4 on 2025-07-15 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aiprompt',
            name='model',
            field=models.CharField(blank=True, help_text='The AI model used to generate the response', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='aiprompt',
            name='tokens_used',
            field=models.IntegerField(default=0, help_text='Number of tokens used in the AI response'),
        ),
    ]
