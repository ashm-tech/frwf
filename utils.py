from __future__ import annotations

import re
import logging
import warnings
from typing import IO, Tuple, Union, BinaryIO, Optional
from datetime import datetime

from furl import furl
from boto3.session import Session as AWSSession
from botocore.config import Config

# Project
from config import S3BucketConfig, settings

logger = logging.getLogger(__name__)


def compact(*args, traverse: bool = False, collapse: bool = False) -> Union[list, dict, tuple]:
    """Compact version of container
    :param traverse: Boolean flag for recursive container lookup
    :param collapse: Boolean flag for remove child containers in traverse mode if length is 0
    """
    # check variadic
    if len(args) == 1:
        obj = args[0]
    else:
        obj = tuple(args)

    # recursive traverse
    def _traverse(_o):
        if not traverse or not isinstance(_o, (list, tuple, dict)):
            return _o
        else:
            _o = compact(_o, traverse=traverse, collapse=collapse)
            if len(_o) == 0 and collapse:
                return None
            return _o

    # compacting
    if isinstance(obj, list):
        result = [_traverse(o) for o in obj if o is not None]
    elif isinstance(obj, tuple):
        result = tuple([_traverse(o) for o in obj if o is not None])
    elif isinstance(obj, dict):
        result = {k: _traverse(v) for k, v in obj.items() if v is not None}
    else:
        result = obj

    # collapse - apply only after main compacting to omit double processing and leave top level object stable
    if collapse:
        result = compact(result)

    return result


class AWSBase:
    def __init__(
        self, aws_access_key_id: Optional[str] = None, aws_secret_access_key: Optional[str] = None, *args, **kwargs
    ):
        # inject default
        aws_access_key_id = aws_access_key_id or settings.LAMB_AWS_ACCESS_KEY
        aws_secret_access_key = aws_secret_access_key or settings.LAMB_AWS_SECRET_KEY

        # Create session
        self._aws_session = AWSSession(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )


class S3Uploader(AWSBase):
    _conn_cfg: S3BucketConfig

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        bucket_url: Optional[str] = None,
        conn_cfg: Optional[S3BucketConfig] = None,
        *args,
        **kwargs,
    ):
        # inject defaults
        if conn_cfg is not None:
            self._conn_cfg = conn_cfg
        else:
            warnings.warn("Use of deprecated S3Uploader args, use S3BucketConfig instead", DeprecationWarning)
            self._conn_cfg = S3BucketConfig(
                bucket_name=bucket_name,
                region_name=region_name,
                access_key=aws_access_key_id,
                secret_key=aws_secret_access_key,
                endpoint_url=endpoint_url,
                bucket_url=bucket_url,
            )

        # process
        super(S3Uploader, self).__init__(
            aws_access_key_id=self._conn_cfg.access_key,
            aws_secret_access_key=self._conn_cfg.secret_key,
            *args,
            **kwargs,
        )

        config_kw = compact(
            {
                "signature_version": "s3v4",
                "connect_timeout": self._conn_cfg.connect_timeout,
                "read_timeout": self._conn_cfg.read_timeout,
            }
        )
        logger.debug(f"boto3 core config would be used: {config_kw}")
        config = Config(**config_kw)
        self._client = self._aws_session.client(
            service_name="s3",
            region_name=self._conn_cfg.region_name,
            endpoint_url=self._conn_cfg.endpoint_url,
            config=config,
        )

        # Check if bucket exists
        if self._conn_cfg.check_buckets_list:
            exist_buckets = [bucket["Name"] for bucket in self._client.list_buckets()["Buckets"]]
            if self._conn_cfg.bucket_name not in exist_buckets:
                logger.warning(f"Have not found S3 {bucket_name} bucket")
                raise ValueError("Requested S3 bucket not exist")

    # properties wrappers
    @property
    def bucket_name(self) -> Optional[str]:
        return self._conn_cfg.bucket_name

    @property
    def bucket_url(self) -> Optional[str]:
        if self._conn_cfg.bucket_url is None:
            if self._conn_cfg.region_name is not None:
                result = f"https://s3.{self._conn_cfg.region_name}.amazonaws.com/{self._conn_cfg.bucket_name}/"
            else:
                result = f"https://{self._conn_cfg.bucket_name}.s3.amazonaws.com/"
        else:
            result = self._conn_cfg.bucket_url
        return result

    @property
    def endpoint_url(self) -> Optional[str]:
        return self._conn_cfg.endpoint_url

    # methods
    def put_object(
        self,
        body: Union[BinaryIO, IO],
        relative_path: str,
        file_type: str,
        private: Optional[bool] = False,
    ) -> str:
        """
        Uploads file to S3

        :param body: binary object to upload
        :param relative_path: relative path to store in
        :param file_type: file content type
        :param private: defines if to store as private file
        :return: uploaded file url
        """
        self._client.put_object(
            Bucket=self.bucket_name,
            ACL="private" if private else "public-read",
            Body=body,
            Key=relative_path,
            ContentType=file_type,
        )
        uploaded_url = furl(self.bucket_url)
        uploaded_url.path.add(relative_path)
        uploaded_url = uploaded_url.url
        logger.info(f"Uploaded S3 URL: {uploaded_url}")
        return uploaded_url

    def delete_object(self, relative_path: str):
        """
        Removes file from S3

        :param relative_path: relative path to stored file
        """
        self._client.delete_object(Bucket=self.bucket_name, Key=relative_path)

    def generate_presigned_url(self, relative_path: str, expires_in: Optional[int] = 3600) -> str:
        """
        Generates presigned url for a stored in S3 file

        :param relative_path: stored file relative path
        :param expires_in: interval of link expiry
        :return: presigned url
        """
        presigned_url = self._client.generate_presigned_url(
            ClientMethod="get_object", Params={"Bucket": self.bucket_name, "Key": relative_path}, ExpiresIn=expires_in
        )
        logger.debug(f"Generated S3 presigned URL: {presigned_url}")
        return presigned_url

    @staticmethod
    def s3_parse_url(url: str) -> Tuple[str, str, str]:
        # TODO: adapt to non AWS s3 storages
        """
        :return: Tuple of aws region name, bucket name, and file path
        """
        patterns = [
            r"^https?://s3.(?P<region>[\w-]+).amazonaws.com/(?P<bucket>[_\.\w-]+)/(?P<path>[/_\.\w-]+)$",
            r"^https?://(?P<bucket>[_\.\w-]+).s3-(?P<region>[\w-]+).amazonaws.com/(?P<path>[/_\.\w-]+)$",
        ]
        bucket_url = getattr(settings, "AWS_BUCKET_URL", None)
        if bucket_url:
            patterns.insert(0, rf"^{bucket_url}/(?P<path>[/_\.\w-]+)$")
        match = None

        for pattern in patterns:
            match = re.match(pattern, url)
            if match:
                break

        if match is None:
            raise ValueError("No S3 url match found")

        if bucket_url:
            try:
                region = match.group("region")
            except IndexError:
                region = None

            try:
                bucket = match.group("bucket")
            except IndexError:
                bucket = None
        else:
            region = match.group("region")
            bucket = match.group("bucket")

        return region, bucket, match.group("path")

    @classmethod
    def remove_by_url(cls, url):
        # TODO: adapt to non AWS s3 storages
        region, bucket, path = cls.s3_parse_url(url)
        s3_uploader = cls(region_name=region, bucket_name=bucket)
        s3_uploader.delete_object(path)
