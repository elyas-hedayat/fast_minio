import strawberry
from typing import List


@strawberry.input
class BucketInput:
    name: str


@strawberry.input
class FileTransferInput:
    source_bucket: str
    destination_bucket: str
    object_list: List[str]


@strawberry.input
class FileRemoveInput:
    object_name: str
