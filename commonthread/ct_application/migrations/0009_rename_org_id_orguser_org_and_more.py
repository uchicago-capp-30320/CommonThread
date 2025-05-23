# Generated by Django 5.2 on 2025-05-14 22:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ct_application", "0008_rename_text_content_story_content_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="orguser",
            old_name="org_id",
            new_name="org",
        ),
        migrations.RenameField(
            model_name="orguser",
            old_name="user_id",
            new_name="user",
        ),
        migrations.RenameField(
            model_name="project",
            old_name="org_id",
            new_name="org",
        ),
        migrations.RenameField(
            model_name="projecttag",
            old_name="proj_id",
            new_name="proj",
        ),
        migrations.RenameField(
            model_name="projecttag",
            old_name="tag_id",
            new_name="tag",
        ),
        migrations.RenameField(
            model_name="story",
            old_name="proj_id",
            new_name="proj",
        ),
        migrations.RenameField(
            model_name="story",
            old_name="content",
            new_name="text_content",
        ),
        migrations.RenameField(
            model_name="storytag",
            old_name="story_id",
            new_name="story",
        ),
        migrations.RenameField(
            model_name="storytag",
            old_name="tag_id",
            new_name="tag",
        ),
        migrations.RemoveField(
            model_name="organization",
            name="org_id",
        ),
        migrations.RemoveField(
            model_name="orguser",
            name="org_user_id",
        ),
        migrations.RemoveField(
            model_name="projecttag",
            name="proj_tag_id",
        ),
        migrations.AddField(
            model_name="customuser",
            name="bio",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="city",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="customuser",
            name="position",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="customuser",
            name="profile",
            field=models.FileField(
                default="profile_pics/default.jpg", upload_to="profile_pics/"
            ),
        ),
        migrations.AddField(
            model_name="organization",
            name="description",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="organization",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AddField(
            model_name="organization",
            name="profile",
            field=models.FileField(
                default="org_pics/default.jpg", upload_to="org_pics/"
            ),
        ),
        migrations.AddField(
            model_name="orguser",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="insight",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="projecttag",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AddField(
            model_name="story",
            name="audio_content",
            field=models.FileField(blank=True, null=True, upload_to="audio/"),
        ),
        migrations.AddField(
            model_name="story",
            name="image_content",
            field=models.FileField(blank=True, null=True, upload_to="images/"),
        ),
        migrations.AddField(
            model_name="story",
            name="summary",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="tag",
            name="created_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="tag",
            name="created_by",
            field=models.TextField(
                choices=[("user", "user"), ("computer", "computer")], null=True
            ),
        ),
        migrations.AddField(
            model_name="tag",
            name="required",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="MLProcessingQueue",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "task_type",
                    models.TextField(
                        choices=[
                            ("tag", "tag"),
                            ("summary", "summary"),
                            ("insight", "insight"),
                        ]
                    ),
                ),
                (
                    "status",
                    models.TextField(
                        choices=[
                            ("processing", "processing"),
                            ("completed", "completed"),
                            ("failed", "failed"),
                        ]
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ct_application.project",
                    ),
                ),
                (
                    "story",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ct_application.story",
                    ),
                ),
            ],
        ),
    ]
