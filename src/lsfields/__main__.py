#!/usr/bin/env python

import argparse
import logging
import os
import urllib.parse
from typing import Generator

import pyarrow.parquet
import boto3

DESCRIPTION = """
This will list all the field names for all the data sets
in a bucket on AWS S3 object storage.
"""

logger = logging.getLogger(__name__)

AWS_PROFILE = os.getenv('AWS_PROFILE', 'default')

session: boto3.session.Session = None
'AWS connection session'
s3_client = None
'AWS S3 service client'


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-l', '--loglevel', default='WARNING')
    parser.add_argument('bucket', help='S3 bucket location URI')
    parser.add_argument('--prefix', required=False, default='')
    parser.add_argument('--no-sign-request', action='store_true')
    parser.add_argument('--profile', default=AWS_PROFILE, help='AWS profile to use')
    return parser.parse_args()


def get_parquet_column_names(bucket: str, key: str):
    """

    """
    # Use pyarrow to access the ParquetDataset
    dataset = pyarrow.parquet.ParquetDataset(f"s3://{bucket}/{key}")

    # Get column names from schema
    return dataset.schema.names


def list_parquet_files(s3_client, bucket: str, prefix: str = None) -> Generator[str, None, None]:
    """
    This function yields the S3 key (path) of parquet files in an S3 bucket as a generator.

    Args:
        s3_client: AWS S3 service client
        bucket: The name of the S3 bucket to search (str).
        prefix: Folder

    Yields:
        The S3 key (path) of each parquet file found (str).
    """
    paginator = s3_client.get_paginator("list_objects_v2")

    logger.info("%s/%s", bucket, prefix)
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        # Loop through S3 objects (files)
        for obj in page.get("Contents", []):
            s3_key: str = obj["Key"]
            if s3_key.endswith(".parquet"):
                yield s3_key


def main():
    global session
    global s3_client

    args = get_args()
    logging.basicConfig(
        format="%(name)s:%(asctime)s:%(levelname)s:%(message)s",
        level=logging.INFO if args.verbose else args.loglevel
    )

    # Connect to AWS
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/session.html
    session = boto3.session.Session(profile_name=args.profile)
    s3_client = session.client('s3')
    for file in list_parquet_files(s3_client, args.bucket, prefix=args.prefix):
        print(file)


if __name__ == '__main__':
    main()
