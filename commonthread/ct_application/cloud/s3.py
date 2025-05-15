from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import boto3

###########################
# TEST 
# (uses env vars AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
s3 = boto3.client("s3")

# with open("test.txt","rb") as f:
#     s3.upload_fileobj(f, "ct-user-profiles", "test.txt")

# print("upload okay")
###########################


class UserProfileStorage(S3Boto3Storage):
    bucket_name = settings.CT_BUCKET_USER_PROFILES

class OrgProfileStorage(S3Boto3Storage):
    bucket_name = settings.CT_BUCKET_ORG_PROFILES

class StoryImageStorage(S3Boto3Storage):
    bucket_name = settings.CT_BUCKET_STORY_IMAGES

class StoryAudioStorage(S3Boto3Storage):
    bucket_name = settings.CT_BUCKET_STORY_AUDIO