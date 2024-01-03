import binascii
import os
from minio import Minio
from minio.commonconfig import CopySource

minio_client = Minio(endpoint="192.168.23.49:9000", access_key="fB7tN1WMnkAPzciqkPOG",
                     secret_key="WxzjBKitDBoBViQLpEhx4LywKyj20PKVxWtwpWJM", secure=False)


def _generate_code():
    return binascii.hexlify(os.urandom(20)).decode('utf-8')


def copy_and_delete_files(*,
                          file_list: list[str],
                          source_bucket: str,
                          destination_bucket: str
                          ) -> None:
    for item in file_list:
        minio_client.copy_object(
            destination_bucket,
            item,
            CopySource(source_bucket, item)  # source bucket/object
        )
        minio_client.remove_object(source_bucket, item)