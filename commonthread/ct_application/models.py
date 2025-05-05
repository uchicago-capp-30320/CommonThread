from django.db import models
from django.db.models import Model 
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
