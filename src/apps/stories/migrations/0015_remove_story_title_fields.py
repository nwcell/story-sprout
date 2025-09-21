# Generated manually to remove orphaned title fields from database

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("stories", "0014_remove_page_content_draft_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE stories_story DROP COLUMN IF EXISTS title_generating;",
            reverse_sql="-- Cannot reverse this operation",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE stories_story DROP COLUMN IF EXISTS title_draft;",
            reverse_sql="-- Cannot reverse this operation",
        ),
    ]
