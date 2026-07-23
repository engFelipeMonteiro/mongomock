"""Tools for specifying BSON codec options."""

import collections
from typing import Any
from typing import cast


try:
    from bson import codec_options as bson_codec_options
    from pymongo.common import _UUID_REPRESENTATIONS
except ImportError:
    bson_codec_options = None  # type: ignore[assignment]
    _UUID_REPRESENTATIONS = None  # type: ignore[assignment]

codec_options: Any = bson_codec_options


class TypeRegistry:
    pass


_fields_list: list[str] = [
    'document_class',
    'tz_aware',
    'uuid_representation',
    'unicode_decode_error_handler',
    'tzinfo',
]

_DEFAULT_TYPE_REGISTRY = codec_options.TypeRegistry()
_fields_list.append('type_registry')

_DEFAULT_DATETIME_CONVERSION = codec_options.DatetimeConversion.DATETIME
_fields_list.append('datetime_conversion')

# New default in Pymongo v4:
# https://pymongo.readthedocs.io/en/stable/examples/uuid.html#unspecified
_DEFAULT_UUID_REPRESENTATION = 0

_CodecOptions = collections.namedtuple('_CodecOptions', cast(tuple[str, ...], tuple(_fields_list)))  # type: ignore[misc]


class CodecOptions(_CodecOptions):
    def __new__(
        cls,
        document_class=dict,
        tz_aware=False,
        uuid_representation=_DEFAULT_UUID_REPRESENTATION,
        unicode_decode_error_handler='strict',
        tzinfo=None,
        type_registry=_DEFAULT_TYPE_REGISTRY,
        datetime_conversion=_DEFAULT_DATETIME_CONVERSION,
    ):
        if not isinstance(tz_aware, bool):
            raise TypeError('tz_aware must be True or False')

        if uuid_representation is None:
            uuid_representation = _DEFAULT_UUID_REPRESENTATION

        values = (
            document_class,
            tz_aware,
            uuid_representation,
            unicode_decode_error_handler,
            tzinfo,
        )

        if 'type_registry' in _fields_list:
            type_registry = type_registry or _DEFAULT_TYPE_REGISTRY
            values += (type_registry,)

        if 'datetime_conversion' in _fields_list:
            datetime_conversion = datetime_conversion or _DEFAULT_DATETIME_CONVERSION
            values += (datetime_conversion,)

        return tuple.__new__(cls, values)

    def with_options(self, **kwargs):
        opts = self._asdict()
        opts.update(kwargs)
        return CodecOptions(**opts)

    def to_pymongo(self):
        if not codec_options:
            return None

        uuid_representation = self.uuid_representation
        if _UUID_REPRESENTATIONS and isinstance(self.uuid_representation, str):
            uuid_representation = _UUID_REPRESENTATIONS[uuid_representation]

        return codec_options.CodecOptions(
            document_class=self.document_class,
            tz_aware=self.tz_aware,
            uuid_representation=uuid_representation,
            unicode_decode_error_handler=self.unicode_decode_error_handler,
            tzinfo=self.tzinfo,
            type_registry=self.type_registry,
            datetime_conversion=self.datetime_conversion,
        )


def is_supported(custom_codec_options):
    if not custom_codec_options:
        return None

    return CodecOptions(**custom_codec_options._asdict())
