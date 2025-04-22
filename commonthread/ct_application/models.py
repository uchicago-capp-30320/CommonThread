from django.db import models
from django.db.models import Model 
from django.contrib.auth.models import User
#Onur: I'm not sure how this User model works, but I'll learn
# https://www.geeksforgeeks.org/how-to-use-user-model-in-django/ 

# Create your models here.
class Organization(Model):
    # we may use autofields https://www.geeksforgeeks.org/autofield-django-models/
    oid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, unique=True) #basically varchar 
    def __str__(self):
        return self.name
    def get_org_id(self):
        return self.oid
    def get_org_name(self):
        return self.name

class Project(Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
     # like a birth certificate, doesnt change
    created_at = models.DateTimeField(auto_now_add=True)
     # if we revert to default key given by django
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    #  creator = models.ForeignKey(User, on_delete=models.CASCADE) # if we want a creator field
    #same project name cant repeat in the same organization
    authorized_users = models.ManyToManyField(User, related_name='authorized_projects')
    class Meta:
         unique_together = ['name', 'organization']

    def __str__(self):
          return self.name
    
class TagName(Model):
    name = models.CharField(max_length=250, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)#do we need this?
    def __str__(self):
          return self.name
     
class ProjectTagName(Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    tag_name = models.ForeignKey(TagName, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['project', 'tag_name']

class Story(Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    text_input = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    #we need to talk about image input
    def __str__(self):
        return self.title
    
class StoryTagValue(Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    tag_name = models.ForeignKey(TagName, on_delete=models.CASCADE)
    value = models.CharField(max_length=250) 

    class Meta:
        unique_together = ['story', 'tag_name']
    
    