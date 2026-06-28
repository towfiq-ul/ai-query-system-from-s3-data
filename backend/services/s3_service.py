import boto3
from botocore.exceptions import ClientError, BotoCoreError
from typing import Generator
from core.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".csv", ".json", ".md"}


class S3Service:
    def __init__(self):
        cfg = get_settings()
        kwargs = dict(
            region_name=cfg.aws_region,
            aws_access_key_id=cfg.aws_access_key_id,
            aws_secret_access_key=cfg.aws_secret_access_key,
        )
        if cfg.aws_endpoint_url:
            logger.info("Using custom S3 endpoint", extra={"endpoint": cfg.aws_endpoint_url})
            kwargs["endpoint_url"] = cfg.aws_endpoint_url
        self._client = boto3.client("s3", **kwargs)
        self._bucket = cfg.s3_bucket_name

    def list_keys(self, prefix: str = "") -> Generator[str, None, None]:
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self._bucket, Prefix=prefix):
            contents = page.get("Contents", [])
            logger.info("S3 page received", extra={"bucket": self._bucket, "prefix": prefix, "count": len(contents)})
            for obj in contents:
                key: str = obj["Key"]
                ext = "." + key.rsplit(".", 1)[-1].lower() if "." in key else ""
                logger.info("S3 key found", extra={"key": key, "ext": ext, "supported": ext in SUPPORTED_EXTENSIONS})
                if ext in SUPPORTED_EXTENSIONS:
                    yield key

    def download_bytes(self, key: str) -> bytes:
        """Download an S3 object and return raw bytes."""
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return response["Body"].read()
        except ClientError as exc:
            error_code = exc.response["Error"]["Code"]
            logger.error("S3 ClientError", extra={"key": key, "code": error_code})
            raise
        except BotoCoreError as exc:
            logger.error("S3 BotoCoreError", extra={"key": key, "error": str(exc)})
            raise
