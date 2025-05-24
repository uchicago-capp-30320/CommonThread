from django.db import models
from django.contrib.auth.models import AbstractUser

# consider use of uniqueconstraints

################################### User/Auth Tables ##########################################


class CustomUser(AbstractUser):
    name = models.CharField("display name", max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, unique=True)
    city = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    position = models.CharField(max_length=100, blank=True)
    profile = models.FileField(upload_to="profile_pics/", default="user_default.jpg")


###################################### Story Tables ##########################################


# organization
class Organization(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(default="")
    profile = models.FileField(upload_to="org_pics/", default="org_default.jpg")


# project
class Project(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    curator = models.ForeignKey(CustomUser, models.SET_NULL, blank=True, null=True)
    date = models.DateField()
    insight = models.TextField(null=True, blank=True)


# story
class Story(models.Model):
    proj = models.ForeignKey(Project, on_delete=models.CASCADE)
    storyteller = models.CharField(max_length=100)
    curator = models.ForeignKey(
        CustomUser, models.SET_NULL, blank=True, null=True
    )  # Just null curator if user is deleted
    date = models.DateField()
    text_content = models.TextField()
    audio_content = models.FileField(upload_to="audio/", null=True, blank=True)
    image_content = models.FileField(upload_to="images/", null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    is_transcript = models.BooleanField(null=True, blank=False)


####################################### TAG TABLES #######################################


# tag
class Tag(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100, null=True, blank=True)  # Allow null values
    required = models.BooleanField()
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.TextField(choices=[('user', 'user'), ('computer', 'computer')], null=True)

# story-tag
class StoryTag(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


# project-tag
class ProjectTag(models.Model):
    proj = models.ForeignKey(Project, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


################################# ADMIN TABLES ############################################


# org-user
class OrgUser(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    access = models.CharField(max_length=20)


################################# ML TABLES ############################################

class MLProcessingQueue(models.Model):
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, null=True, on_delete=models.CASCADE)
    task_type = models.TextField(choices=[('tag', 'tag'), ('summary', 'summary'), ('insight', 'insight')])
    status = models.TextField(choices=[('processing', 'processing'), ('completed', 'completed'), ('failed', 'failed')])
    timestamp = models.DateTimeField(auto_now_add=True)