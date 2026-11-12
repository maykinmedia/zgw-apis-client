from collections.abc import Sequence
from typing import dataclass_transform

from msgspec import UNSET, Struct, StructMeta, UnsetType


def _to_camel(name: str) -> str:
    """
    Like msgspec's ``rename="camel"``, but keeps the ``__`` of lookups such as
    ``rol__betrokkene_identificatie__medewerker__identificatie``.
    """
    segments = []
    for segment in name.split("__"):
        first, *rest = segment.split("_")
        segments.append(first + "".join(part.capitalize() for part in rest))
    return "__".join(segments)


@dataclass_transform(kw_only_default=True)
class SchemaStructMeta(StructMeta):
    """
    Configure the behaviour of structs used to interface with the ZGW APIs.

    The metaclass avoids having to repeat a bunch of keyword arguments when defining
    msgspec structs. In particular, we establish:

    * Forbid positional arguments - many resources have a lot of properties with the -
      enforcing keyword arguments helps readability and makes things more explicit.
    * Apply conversion between camel case and snake case, see :func:`_to_camel`.
    """

    def __new__(cls, name, bases, namespace, **struct_config):
        struct_config["kw_only"] = True
        struct_config["rename"] = _to_camel
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
