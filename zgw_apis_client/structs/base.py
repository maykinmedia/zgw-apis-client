from collections.abc import Sequence
from typing import dataclass_transform

from msgspec import UNSET, Struct, StructMeta, UnsetType


@dataclass_transform(kw_only_default=True)
class SchemaStructMeta(StructMeta):
    """
    Configure the behaviour of structs used to interface with the Open Product API.

    The metaclass avoids having to repeat a bunch of keyword arguments when defining
    msgspec structs. In particular, we establish:

    * Forbid positional arguments - many resources have a lot of properties with the -
      enforcing keyword arguments helps readability and makes things more explicit.
    * Apply conversion between camel case and snake case.
    """

    def __new__(cls, name, bases, namespace, **struct_config):
        struct_config["kw_only"] = True
        struct_config["rename"] = "camel"
        return super().__new__(cls, name, bases, namespace, **struct_config)


class BaseSchemaStruct(Struct, metaclass=SchemaStructMeta):
    """
    Base class for any struct definition used in the client.

    The base class must be used to model API resources, response shapes, (query)
    parameters... Essentially anything that lives under the ``components`` key in the
    OpenAPI specification must inherit from this base class.
    """


class PaginationParams(BaseSchemaStruct):
    page: int | UnsetType = UNSET
    page_size: int | UnsetType = UNSET


class PaginatedResponseBody[T: BaseSchemaStruct](BaseSchemaStruct):
    count: int
    next: str | None
    previous: str | None
    results: Sequence[T]
