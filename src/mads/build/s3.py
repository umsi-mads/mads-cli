"""Common tools for interacting with AWS S3."""

import boto3

s3 = boto3.client("s3")


def __getattr__(name):
    return getattr(s3, name)


def find_keys(
    bucket: str,
    prefix: str = "",
    contains: list[str] = [],
) -> list[str]:
    list_objects = s3.get_paginator("list_objects_v2")
    paginator = list_objects.paginate(Bucket=bucket, Prefix=prefix)

    results = []

    if contains and not isinstance(contains, list):
        contains = [contains]

    if contains:
        queries = [f"contains(Key, '{term}')" for term in contains]
        search = f"Contents[?{' && '.join(queries)}].Key"
        results = paginator.search(search)
    else:
        results = [
            entry.get("Key") for page in paginator for entry in page.get("Contents", [])
        ]

    return list(results)


def find_key(
    bucket: str,
    prefix: str = "",
    contains: list[str] = [],
) -> str | None:
    for key in find_keys(bucket, prefix, contains):
        return key
    return None


def presign(
    bucket: str,
    keys: str | list[str],
    expires_in: int = 12 * 60 * 60,  # 12 hours
) -> dict[str, str]:
    if isinstance(keys, str):
        keys = [keys]

    return {
        key: s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        for key in keys
    }


def read_key(bucket: str, key: str) -> str:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode()


def head(bucket: str, key: str) -> dict:
    return s3.head_object(Bucket=bucket, Key=key)
