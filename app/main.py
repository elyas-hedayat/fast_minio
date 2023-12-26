import io
from typing import Optional
import strawberry
from fastapi import FastAPI

from minio.commonconfig import CopySource, Tags
from starlette.middleware.cors import CORSMiddleware
from strawberry.asgi import GraphQL
from strawberry.file_uploads import Upload
from strawberry.types import Info

from app.inputs import BucketInput, FileTransferInput
from app.types import Message
from app.utils import minio_client, _generate_code
from .response import Response
from . import status


@strawberry.type
class Query:
    @strawberry.field
    async def make_bucket(self, info: Info, bucket_name: str) -> Optional[Message]:
        try:
            minio_client.make_bucket(bucket_name=bucket_name)
            return Message(message=Response.BUCKET_CREATE_SUCCESS.value, status_code=status.HTTP_SUCCESS)
        except Exception as e:
            return Message(message=Response.BUCKET_CREATE_ERROR.value, status_code=status.HTTP_ERROR)

    @strawberry.field
    async def bucket_exists(self, info: Info, bucket_name: str) -> Optional[Message]:
        bucket_exist = minio_client.bucket_exists(bucket_name)
        return Message(message=bucket_exist, status_code=status.HTTP_SUCCESS)

    @strawberry.field
    async def list_buckets(self, info: Info) -> Optional[Message]:
        buckets = minio_client.list_buckets()
        return Message(message=buckets, status_code=status.HTTP_SUCCESS)

    @strawberry.field
    async def list_objects(self, info: Info, bucket_name: str) -> Optional[Message]:
        objects = minio_client.list_objects(bucket_name=bucket_name)
        return Message(message=objects, status_code=status.HTTP_SUCCESS)

    @strawberry.field
    def get_object(self, info: Info, object_name: str) -> Optional[Message]:
        try:
            bucket_name = "profile"
            response = minio_client.get_object(bucket_name=bucket_name, object_name=object_name)
            url = "http://192.168.23.49:9000"
            return Message(message=url + response.url, status_code=1200)
        except Exception as e:
            return Message(message=str(e), status_code=1400)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def remove_bucket(self, info: Info, input: BucketInput) -> Optional[Message]:
        try:
            minio_client.remove_bucket(input.name)
            return Message(message=Response.BUCKET_REMOVED.value, status_code=status.HTTP_SUCCESS)
        except Exception as e:
            return Message(message=str(e), status_code=status.HTTP_ERROR)

    @strawberry.mutation
    async def user_put_object(self, info: Info, file: Upload, token: str) -> Optional[Message]:
        try:
            object_id = _generate_code() + file.filename
            file_object = await file.read()
            tags = Tags(for_object=True)
            tags["user_token"] = token
            response = minio_client.put_object("temp", object_id, io.BytesIO(file_object), length=-1,
                                               part_size=10 * 1024 * 1024, tags=tags)
            return Message(message=Response.SUCCESS_UPLOAD.value, id=response.object_name,
                           status_code=status.HTTP_SUCCESS)
        except Exception as e:
            return Message(message=Response.FAIL_UPLOAD.value, status_code=status.HTTP_ERROR)

    @strawberry.mutation
    async def transfer_bucket(self, info: Info, input: FileTransferInput) -> Optional[Message]:
        source_exists = minio_client.bucket_exists(input.source_bucket)
        destination_exists = minio_client.bucket_exists(input.destination_bucket)

        if not (source_exists and destination_exists):
            return Message(detail=Response.BUCKET_NOT_EXISTS.value)
        try:
            for item in input.object_list:
                minio_client.copy_object(
                    input.destination_bucket,
                    item,
                    CopySource(input.source_bucket, item)  # source bucket/object
                )
                minio_client.remove_object(input.source_bucket, item)
            return Message(message=Response.SUCCESS_TRANSFER.value, status_code=status.HTTP_SUCCESS)
        except Exception as e:
            return Message(message=str(e), status_code=status.HTTP_ERROR)

    @strawberry.mutation
    async def user_remove_object(self, info: Info, object_name: str, token: str) -> Optional[Message]:
        try:
            minio_client.remove_object("temp", object_name)
            return Message(message=Response.SUCCESS_DELETE.value, status_code=status.HTTP_SUCCESS)
        except Exception as e:
            return Message(message=Response.FAIL_DELETE.value, status_code=status.HTTP_ERROR)


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQL(schema)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
