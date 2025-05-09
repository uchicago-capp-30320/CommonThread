from django.db import models
from django.contrib.auth.models import AbstractUser

# consider use of uniqueconstraints

################################### User/Auth Tables ##########################################


class CustomUser(AbstractUser):
    name = models.CharField("display name", max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, unique=True)


# user-login  ########### SUNSET IN FAVOR OF DJANGO PASSWORD STORAGE ###################
#class UserLogin(models.Model):
#    user_id = models.OneToOneField(
#        CustomUser, primary_key=True, on_delete=models.CASCADE
#    )
#    username = models.CharField(max_length=255, unique=True)
#    password = models.CharField(
#        max_length=255
#    )  # This probably changes based on PW storage method


###################################### Story Tables ##########################################


# organization
class Organization(models.Model):
    name = models.CharField(max_length=200)


# project
class Project(models.Model):
    org_id = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    curator = models.ForeignKey(CustomUser, models.SET_NULL, blank=True, null=True)
    date = models.DateField()


# story
class Story(models.Model):
    proj_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    storyteller = models.CharField(max_length=100)
    curator = models.ForeignKey(
        CustomUser, models.SET_NULL, blank=True, null=True
    )  # Just null curator if user is deleted
    date = models.DateField()
    content = models.TextField()


####################################### TAG TABLES #######################################


# tag
class Tag(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100, null=True, blank=True)  # Allow null values

# story-tag
class StoryTag(models.Model):
    story_id = models.ForeignKey(Story, on_delete=models.CASCADE)
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)


# project-tag
class ProjectTag(models.Model):
    proj_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)


################################# ADMIN TABLES ############################################


# org-user
class OrgUser(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    org_id = models.ForeignKey(Organization, on_delete=models.CASCADE)
    access = models.CharField(max_length=20)
