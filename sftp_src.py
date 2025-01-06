import paramiko
from paramiko import ECDSAKey, RSAKey
from src import read_config_file,get_secret
from io import StringIO
import os
from io import BytesIO
import boto3


def create_sftp_connection():
    """
    Initiate SFTP connection
    :return sftp client:
    """
    bucket_name = "<your-bucket-name>"
    config_file_key = "<config-file-key>"
    secret_name = "<secret-name>"
  
    # Reading from config JSON or secret manager are just two ways of getting the credentials.
    # Feel free to use any other method of getting the SFTP credentials and incorporating here.
    # If config file
    sftp_credentials = read_config_file(bucket_name, config_file_key)
    # OR if secrets manager
    sftp_credentials = get_secret(secret_name)
    
    hostname = sftp_credentials['hostname']
    port = sftp_credentials['port']
    username = sftp_credentials['username']

    try:
        # Initialize the SSH transport
        transport = paramiko.Transport((hostname, port))
        # Determine the authentication method based on the credentials provided
        if 'password' in sftp_credentials:
            # Connect using password authentication
            transport.connect(username=username, password=sftp_credentials['password'])
        else:
            # Connect using private key authentication
            key = sftp_credentials['private_key']
            # Load the private key. Determine the type from the key structure.
            if key.startswith("-----BEGIN EC PRIVATE KEY-----"):
                private_key = ECDSAKey(file_obj=StringIO(key))
            elif key.startswith("-----BEGIN RSA PRIVATE KEY-----"):
                private_key = RSAKey(file_obj=StringIO(key))
            else:
                raise ValueError("Unsupported key type")
            
            transport.connect(username=username, pkey=private_key)
        # Check if the transport is active
        if transport.is_active():
            sftp_client = paramiko.SFTPClient.from_transport(transport)
            return sftp_client
      
    except Exception as e:
        print(f"Failed to connect to SFTP: {e}")
        return None



def upload_files_to_s3_from_sftp(sftp_directory, s3_bucket, s3_directory):
    """
    Upload all files from an SFTP directory to an S3 bucket.

    :param sftp_directory: Path to the SFTP directory containing files
    :param s3_bucket: Target S3 bucket name
    :param s3_directory: Target directory path in S3 bucket
    """
    s3_client = boto3.client('s3')
    sftp_client = None
    try:
        # Create SFTP connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname='your_sftp_host',
            username='your_username',
            password='your_password'
            # Alternative: key_filename='path/to/private/key'
        )
        sftp_client = ssh_client.open_sftp()

        # List and upload files
        files = sftp_client.listdir(sftp_directory)
        for filename in files:
            remote_filepath = os.path.join(sftp_directory, filename)
            s3_object_path = os.path.join(s3_directory, filename)
            with sftp_client.file(remote_filepath, 'rb') as remote_file:
                file_data = remote_file.read()
            file_obj = BytesIO(file_data)
            s3_client.upload_fileobj(file_obj, s3_bucket, s3_object_path)
            
    except Exception as e:
        print(f"Failed to upload files: {str(e)}")
    finally:
        if sftp_client:
            sftp_client.close()
            ssh_client.close()


