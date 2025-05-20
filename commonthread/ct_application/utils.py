from commonthread.settings import JWT_SECRET_KEY,JWT_REFRESH_SECRET_KEY
import datetime
import jwt
import boto3
from django.conf import settings
from typing import Optional

def generate_s3_presigned(
    bucket_name: str,
    key: str,
    operation: str,
    content_type: Optional[str] = None,
    expiration: int = 3600
) -> dict:
    """
    Generate S3 presigned POST (upload) or GET (download).
    """
    client = boto3.client(
        "s3",
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    if operation == "upload":
        if not content_type:
            raise ValueError("content_type is required for upload")
        return client.generate_presigned_post(
            Bucket=bucket_name,
            Key=key,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"acl": "private"},
                {"Content-Type": content_type},
                ["eq", "$key", key],
            ],
            ExpiresIn=expiration,
        )

    if operation == "download":
        url = client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=expiration,
        )
        return {"url": url}

    raise ValueError(f"Unsupported operation: {operation}")

def generate_access_token(user_id:int)-> str:
    payload = {
        'sub': str(user_id),
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours = 2),
        'iat': datetime.datetime.now(datetime.timezone.utc)
    }
    return jwt.encode(payload,JWT_SECRET_KEY,algorithm = 'HS256')

def generate_refresh_token(user_id:int)-> str:
    payload = {
        'sub': str(user_id),
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
        'iat': datetime.datetime.now(datetime.timezone.utc)
    }
    return jwt.encode(payload,JWT_REFRESH_SECRET_KEY,algorithm ='HS256')

def decode_refresh_token(token):
    return jwt.decode(token,JWT_REFRESH_SECRET_KEY,
                      algorithms =['HS256'],
                      options={"require_exp": True, "verify_exp": True}
                      )
                      
def decode_access_token(token):
    return jwt.decode(token,JWT_SECRET_KEY,
                      algorithms =['HS256'],
                      options={"require_exp": True, "verify_exp": True}
                      )


                    

