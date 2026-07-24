from enum import StrEnum

from .http_method import SirenHttpMethod


class SirenActionMethod(StrEnum):
    DELETE = SirenHttpMethod.DELETE.value
    GET = SirenHttpMethod.GET.value
    PATCH = SirenHttpMethod.PATCH.value
    POST = SirenHttpMethod.POST.value
    PUT = SirenHttpMethod.PUT.value
