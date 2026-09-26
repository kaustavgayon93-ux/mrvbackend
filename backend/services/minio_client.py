import logging
import boto3
from botocore.exceptions import ClientError
from typing import List, Optional

logger = logging.getLogger(__name__)

class MinIOStorageClient:
    """
    MinIO/S3 Storage Client.
    """

    def __init__(self, endpoint_url: str, access_key: str, secret_key: str, region_name: str = 'us-east-1'):
        """
        Initialize the MinIO client using boto3.
        """
        self.endpoint_url = endpoint_url
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
            config=boto3.session.Config(signature_version='s3v4')
        )

    def ensure_bucket_exists(self, bucket_name: str) -> None:
        """
        Create bucket if it does not exist.
        """
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    self.s3_client.create_bucket(Bucket=bucket_name)
                    logger.info(f"Created bucket {bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket {bucket_name}: {str(create_error)}")
                    raise
            else:
                logger.error(f"Error checking bucket {bucket_name}: {str(e)}")
                raise

    def upload_file(self, local_path: str, bucket: str, object_key: str, content_type: Optional[str] = None) -> str:
        """
        Upload a file to MinIO and return its S3 URI.
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
                
            self.s3_client.upload_file(local_path, bucket, object_key, ExtraArgs=extra_args)
            s3_uri = f"s3://{bucket}/{object_key}"
            logger.info(f"Successfully uploaded {local_path} to {s3_uri}")
            return s3_uri
        except ClientError as e:
            logger.error(f"Failed to upload {local_path} to {bucket}/{object_key}: {str(e)}")
            raise

    def download_file(self, bucket: str, object_key: str, local_path: str) -> str:
        """
        Download a file from MinIO.
        """
        try:
            self.s3_client.download_file(bucket, object_key, local_path)
            logger.info(f"Successfully downloaded {bucket}/{object_key} to {local_path}")
            return local_path
        except ClientError as e:
            logger.error(f"Failed to download {bucket}/{object_key}: {str(e)}")
            raise

    def generate_presigned_url(self, bucket: str, object_key: str, expires_in: int = 3600) -> str:
        """
        Generate a presigned URL for an object.
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': object_key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {bucket}/{object_key}: {str(e)}")
            raise

    def list_objects(self, bucket: str, prefix: str = '') -> List[dict]:
        """
        List objects in a bucket with a given prefix.
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            return response.get('Contents', [])
        except ClientError as e:
            logger.error(f"Failed to list objects in {bucket} with prefix '{prefix}': {str(e)}")
            raise

    def delete_object(self, bucket: str, object_key: str) -> None:
        """
        Delete an object from a bucket.
        """
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=object_key)
            logger.info(f"Successfully deleted {bucket}/{object_key}")
        except ClientError as e:
            logger.error(f"Failed to delete {bucket}/{object_key}: {str(e)}")
            raise
