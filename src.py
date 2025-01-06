import boto3
import json
from botocore.session import Session
from boto3 import session
def get_aws_clients():
    """
    Get the AWS clients associated with a service
    Include more services based on requirements
    """
    s3_config = {'service_name': 's3', 'region_name': '<your-aws-region>'}
    s3_client = boto3.client(**s3_config)

    return s3_client
s3_client = get_aws_clients() # Declare as global object so that we can access from other functions


def read_config_file(bucket_name, config_file_key):
    """
    Read config file from S3
    :param bucket_name: Name of the S3 bucket where the config file is stored
    :param config_file_key: Path of the file within the bucket
    """
    try:
        config_object = s3_client.get_object(Bucket=bucket_name, Key=config_file_key)
        config_content = config_object['Body'].read()
        config = json.loads(config_content)
        return config
    except Exception as e:
        raise Exception(f'{config_file_key} not found in bucket {bucket_name}')
    

def get_secret(secret_name):
    """
    Read secret from AWS Secrets Manager
    :param secret_name:Name of the secret instance which holds the SFTP credentials
    :return secret: Dictionary of credentials
    """
    region_name = "<region-name>"
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )

    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    else:
        raise Exception("Secret not found")
    

