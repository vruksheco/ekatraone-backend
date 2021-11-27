"""
This file is for s3 services
such as
upload file to s3
create pressigned url for the file
"""

import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
from datetime import timedelta
import config

s3_signature = {'v4':'s3v4','v2':'s3'}

def create_presigned_url(bucket_name, object_name, expiration=3600,signature_version=s3_signature['v4']):
    """
    Generate a presigned url to share an s3 object
    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for presigned url remains valid
    :return: presigned url as a string
    """
    s3_client = boto3.client('s3',
                             aws_access_key_id=config.AWS_ACCESS_KEY,
                             aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                             config=Config(signature_version=signature_version),
                             region_name=config.AWS_DEFAULT_REGION)
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket':bucket_name,
                                                            'Key':object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        return {'message':str(e)}
    return response


def upload_file(file_name, bucket, object_name=None,signature_version=s3_signature['v4'],content_type=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3',
                             aws_access_key_id=config.AWS_ACCESS_KEY,
                             aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                             config=Config(signature_version=signature_version),
                             region_name=config.AWS_DEFAULT_REGION)
    try:
        response = s3_client.upload_file(file_name, bucket, object_name,
                                         ExtraArgs={'ContentType': content_type})
    except ClientError as e:
        return False
    return response