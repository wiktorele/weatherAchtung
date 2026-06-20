import boto3
from typing import Any
from weather_alerts.config.settings import settings


def get_aws_client(service_name: str) -> Any:
    """
    Returns a configured boto3 client for the requested service.
    Handles local development overrides (LocalStack).
    """
    region_name = settings.aws_region
    endpoint_url = None

    if settings.use_local_aws:
        endpoint_url = settings.local_aws_endpoint

    return boto3.resource(
        service_name,
        region_name=region_name,
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.aws_access_key_id or "test",
        aws_secret_access_key=settings.aws_secret_access_key or "test",
    )


def get_sns_client() -> Any:
    """Returns a boto3 client (not resource) for SNS"""
    endpoint_url = None
    if settings.use_local_aws:
        endpoint_url = settings.local_aws_endpoint

    return boto3.client(
        "sns",
        region_name=settings.aws_region,
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.aws_access_key_id or "test",
        aws_secret_access_key=settings.aws_secret_access_key or "test",
    )