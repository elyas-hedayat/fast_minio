from enum import Enum


class Response(Enum):
    BUCKET_CREATE_SUCCESS = "باکت با موفقیت ساخته شد"
    BUCKET_CREATE_ERROR = "خطا در ساخت باکت"
    BUCKET_REMOVED = "باکت با موفقیت حذف شد"
    SUCCESS_UPLOAD = "فایل با موفقیت باگذاری شد"
    FAIL_UPLOAD = "خطلا در بارگذاری فایل"
    BUCKET_NOT_EXISTS = "Source or destination bucket does not exist"
    SUCCESS_TRANSFER = "Objects copied successfully and removed from temp bucket."
    SUCCESS_DELETE = "فایل با موفقیت حذف شد"
    FAIL_DELETE = "خطلا در حذف فایل"
