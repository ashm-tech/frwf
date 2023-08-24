from __future__ import annotations

import dataclasses
from typing import Any, Optional, TypedDict

from pydantic import PostgresDsn, BaseSettings, validator

__all__ = [
    "settings",
    "log_config",
]


@dataclasses.dataclass
class S3BucketConfig:
    bucket_name: Optional[str] = None
    region_name: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    endpoint_url: Optional[str] = None
    bucket_url: Optional[str] = None
    check_buckets_list: bool = True
    connect_timeout: Optional[float] = None
    read_timeout: Optional[float] = None

    def response_encode(self, request=None) -> dict:
        return dataclasses.asdict(self)


class Settings(BaseSettings):
    # general
    LOGGING_LEVEL: str
    LOGGING_FORMAT: str
    # kafka
    KAFKA_HOST: str
    KAFKA_PORT: str
    # scrapper agent configs
    SC_APP_NAME: str
    SC_TOPIC_NAME: str
    SC_CONCURRENCY: int = 1
    SC_PARTITIONS: int = 1
    SC_MAXIMUM_PARSING_PAGES: Optional[int] = None
    # scrapper result
    SCR_APP_NAME: str
    SCR_TOPIC_NAME: str
    SCR_CONCURRENCY: int = 1
    SCR_PARTITIONS: int = 1
    # elastic upload
    ELUP_APP_NAME: str
    ELUP_TOPIC_NAME: str
    ELUP_CONCURRENCY: int = 1
    ELUP_PARTITIONS: int = 1
    ES_HOST: str
    ES_PORT: str
    ELASTIC_PASSWORD: str
    # download images
    ID_APP_NAME: str
    ID_TOPIC_NAME: str
    ID_CONCURRENCY: int = 1
    ID_PARTITIONS: int = 1
    # delete images
    DI_APP_NAME: str
    DI_TOPIC_NAME: str
    DI_CONCURRENCY: int = 1
    DI_PARTITIONS: int = 1
    # DB
    FRWF_POSTGRES_HOST: str
    FRWF_POSTGRES_PORT: str
    FRWF_POSTGRES_USER: str
    FRWF_POSTGRES_PASSWORD: str
    FRWF_POSTGRES_DB_NAME: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("FRWF_POSTGRES_USER"),
            password=values.get("FRWF_POSTGRES_PASSWORD"),
            host=values.get("FRWF_POSTGRES_HOST"),
            port=values.get("FRWF_POSTGRES_PORT"),
            path=f"/{values.get('FRWF_POSTGRES_DB_NAME') or ''}",
        )

    MINIO_IMG_BUCKET: str
    MINIO_IMG_ACCESS_KEY: str
    MINIO_IMG_SECRET_KEY: str
    MINIO_IMG_ENDPOINT_URL: str
    MINIO_IMG_BUCKET_URL: str
    MINIO_TIMEOUT_CONNECT: float = 3.0
    MINIO_TIMEOUT_READ: float = 10.0
    AWS_BUCKETS: Optional[object] = None

    @validator("AWS_BUCKETS", pre=True)
    def assemble_aws_buckets(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        return {
            "img": S3BucketConfig(
                bucket_name=values.get("MINIO_IMG_BUCKET"),
                access_key=values.get("MINIO_IMG_ACCESS_KEY"),
                secret_key=values.get("MINIO_IMG_SECRET_KEY"),
                endpoint_url=values.get("MINIO_IMG_ENDPOINT_URL"),
                bucket_url=values.get("MINIO_IMG_BUCKET_URL"),
                check_buckets_list=False,
                connect_timeout=values.get("MINIO_TIMEOUT_CONNECT"),
                read_timeout=values.get("MINIO_TIMEOUT_READ"),
            ),
        }

    class Config:
        case_sensitive = True


settings = Settings()


log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": settings.LOGGING_FORMAT,
        },
    },
    "handlers": {
        "default": {
            "formatter": "simple",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": settings.LOGGING_LEVEL,
        },
    },
}
