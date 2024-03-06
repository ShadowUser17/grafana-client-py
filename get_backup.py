import os
import sys
import boto3
import pathlib
import logging
import argparse
import traceback

# DEBUG_MODE
# AWS_ENDPOINT_URL
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY


def get_object_data(client: any, bucket: str, file: str) -> bytes:
    response = client.get_object(Bucket=bucket, Key=file)
    return response["Body"].read()


def put_file_data(file_name: str, data: bytes) -> None:
    file = pathlib.Path(file_name)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.touch(exist_ok=True)
    file.write_bytes(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("bucket", help="Set bucket name.")
    parser.add_argument("path", help="Set destination file path.")
    return parser.parse_args()


try:
    log_level = logging.DEBUG if os.environ.get("DEBUG_MODE", "") else logging.INFO
    logging.basicConfig(
        format=r'%(levelname)s [%(asctime)s]: "%(message)s"',
        datefmt=r'%Y-%m-%d %H:%M:%S', level=log_level
    )

    args = parse_args()
    client = boto3.client("s3")

    file_name = pathlib.Path(args.path).name
    logging.info("Get s3://{}/{} -> ./{}".format(args.bucket, args.path, file_name))
    data = get_object_data(client, args.bucket, args.path)
    put_file_data(file_name, data)

except Exception:
    logging.error(traceback.format_exc())
    sys.exit(1)
