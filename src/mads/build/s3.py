"""Common tools for interacting with AWS S3."""

import boto3


def find_keys(
    bucket: str,
    prefix: str = "",
    contains: list[str] = [""],
) -> list[str]:
    list_objects = boto3.client("s3").get_paginator("list_objects_v2")
    paginator = list_objects.paginate(Bucket=bucket, Prefix=prefix)
    queries = [f"contains(Key, '{term}')" for term in contains]
    search = f"Contents[?{' && '.join(queries)}].Key"
    results = paginator.search(search)

    return list(results)


def find_key(
    bucket: str,
    prefix: str = "",
    contains: list[str] = [""],
) -> str | None:
    for key in find_keys(bucket, prefix, contains):
        return key
    return None
