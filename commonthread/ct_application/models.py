from django.db import models


################################### User/Auth Tables ##########################################

# user
class User(models.Model):
    user_id = models.AutoField(primary_key = True)
    name = models.CharField("display name", max_length = 30)

# user-login
class UserLogin(models.Model):
    user_id = models.ForeignKey(User, primary_key = True, on_delete = models.CASCADE)
    username = models.CharField(max_length = 255, unique = True)
    password = models.CharField(max_length = 255) # This probably changes based on PW storage method

###################################### Story Tables ##########################################

# organization
class Organization(models.Model):
    org_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name
    def get_id(self):
        return self.org_id
    def get_name(self):
        return self.name
    
# project
class Project(models.Model):
    proj_id = models.AutoField(primary_key=True)
    org_id = models.ForeignKey(Organization, to_field = 'org_id', on_delete = models.CASCADE)
    name = models.CharField(max_length=100) 
    curator = models.ForeignKey(User, models.SET_NULL, blank = True, null = True, to_field = 'user_id')
    date = models.DateField()

# story
class Story(models.Model):
    story_id = models.AutoField(primary_key=True)
    proj_id = models.ForeignKey(Project, to_field = 'proj_id', on_delete = models.CASCADE)
    org_id = models.ForeignKey(Organization, to_field = 'org_id', on_delete = models.CASCADE)
    storyteller = models.CharField(max_length = 100)
    curator = models.ForeignKey(User, models.SET_NULL, blank = True, null = True, to_field = 'user_id') #Just null curator if user is deleted
    date = models.DateField()
    content = models.TextField()

####################################### TAG TABLES #######################################

# tag
class Tag(models.Model):
    tag_id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 100)

# story-tag
class StoryTag(models.Model):
    story_tag_id = models.AutoField(primary_key = True)
    story_id = models.ForeignKey(Story, to_field = 'story_id', on_delete = models.CASCADE)
    tag_id = models.ForeignKey(Tag, to_field = 'tag_id', on_delete = models.CASCADE)

# project-tag
class ProjectTag(models.Model):
    proj_tag_id = models.AutoField(primary_key = True)
    proj_id = models.ForeignKey(Project, to_field = 'proj_id', on_delete = models.CASCADE)
    tag_id = models.ForeignKey(Tag, to_field = 'tag_id', on_delete = models.CASCADE)


################################# ADMIN TABLES ############################################

# org-user
class OrgUser(models.Model):
    org_user_id = models.AutoField(primary_key = True)
    user_id = models.ForeignKey(User, to_field = 'user_id', on_delete = models.CASCADE)
    org_id = models.ForeignKey(Organization, to_field = 'org_id', on_delete = models.CASCADE)
    access = models.CharField(max_length = 20)