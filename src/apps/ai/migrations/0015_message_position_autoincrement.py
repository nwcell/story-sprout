# Generated migration for Message position field changes

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ai", "0014_alter_message_conversation"),
    ]

    operations = [
        # Make position field nullable for bulk_create compatibility
        migrations.AlterField(
            model_name="message",
            name="position",
            field=models.IntegerField(
                null=True,
                blank=True,
                help_text="Auto-assigned sequential position within conversation"
            ),
        ),
    ]
