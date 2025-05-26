from commonthread.settings import JWT_SECRET_KEY,JWT_REFRESH_SECRET_KEY
import datetime
import jwt
import boto3
from django.conf import settings
from typing import Optional
from django.utils import timezone
from django.http import JsonResponse

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
        
        fields = {
            "Content-Type": content_type,
            "success_action_status": "200",
            "key": key,
        }
        conditions = [
            {"acl": "private"},
            ["eq", "$key", key],
            ["eq", "$Content-Type", content_type],
            ["eq", "$success_action_status", "200"],
        ]
        return client.generate_presigned_post(
            Bucket=bucket_name,
            Key=key,
            Fields=fields,
            Conditions=conditions,
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


                    


# Authentication & Authorization Errors (4xx)
AUTH_ERRORS = {
    'NO_TOKEN': (401, "No token provided"),
    'INVALID_TOKEN': (401, "Invalid token"),
    'ACCESS_TOKEN_EXPIRED': (299, "Access token has expired"), 
    'REFRESH_TOKEN_EXPIRED': (401, "Refresh token has expired"),
    'INSUFFICIENT_PERMISSIONS': (403, "Insufficient permissions for this operation"),
    'USER_NOT_IN_ORG': (403, "User is not a member of this organization"),
    'INVALID_CREDENTIALS': (401, "Invalid username or password"),
}

# Resource Errors (4xx)
RESOURCE_ERRORS = {
    'NOT_FOUND': (404, "Resource not found"),
    'ALREADY_EXISTS': (409, "Resource already exists"),
    'STORY_NOT_FOUND': (404, "Story not found"),
    'PROJECT_NOT_FOUND': (404, "Project not found"),
    'ORG_NOT_FOUND': (404, "Organization not found"),
    'USER_NOT_FOUND': (404, "User not found"),
    "INVALID_QUERY_PARAM": (400, "Invalid query parameter."), 
    "BAD_FILTER": (400, "Specify exactly one of org_id, project_id, story_id, or user_id.")
}

# Validation Errors (4xx)
VALIDATION_ERRORS = {
    'INVALID_JSON': (400, "Invalid JSON format"),
    'MISSING_REQUIRED_FIELDS': (400, "Missing required fields"),
    'INVALID_FIELD_FORMAT': (400, "Invalid field format"),
    'INVALID_DATE_FORMAT': (400, "Invalid date format"),
    'INVALID_FILE_TYPE': (400, "Invalid file type"),
    'INVALID_TAG_FORMAT': (400, "Invalid tag format"),
}

# Business Logic Errors (4xx)
BUSINESS_ERRORS = {
    'DUPLICATE_USERNAME': (409, "Username already exists"),
    'DUPLICATE_ORG_NAME': (409, "Organization name already exists"),
    'INVALID_STATE_TRANSITION': (422, "Invalid state transition"),
    'ML_QUEUE_FAILED': (422, "Failed to queue ML processing"),
    'TAG_LIMIT_EXCEEDED': (422, "Tag limit exceeded"),
}

# Server Errors (5xx)
SERVER_ERRORS = {
    'INTERNAL_ERROR': (500, "Internal server error"),
    'DATABASE_ERROR': (503, "Database operation failed"),
    'S3_ERROR': (503, "S3 operation failed"),
    'ML_SERVICE_ERROR': (503, "ML service unavailable"),
    'QUEUE_SERVICE_ERROR': (503, "Queue service unavailable"),
}

def create_error_response(error_type, error_dict, additional_details=None):
    """
    Creates a standardized error response
    
    Args:
        error_type (str): The specific error code from error dictionaries
        error_dict (dict): The error dictionary containing the mapping
        additional_details (dict, optional): Additional error context
    """
    status_code, default_message = error_dict[error_type]
    
    error_response = {
        "success": False,
        "error": {
            "code": error_type,
            "message": default_message,
            "timestamp": timezone.now().isoformat()
        }
    }
    
    if additional_details:
        error_response["error"]["details"] = additional_details
        
    return JsonResponse(error_response, status=status_code)