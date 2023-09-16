from collections import ChainMap
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Type, TypeVar

T = TypeVar("T")


class DataClassMixins(object):
    def as_dict(self) -> Dict[str, Any]:
        assert is_dataclass(self) and not isinstance(self, type)
        return asdict(self)

    def as_cls(self, cls: Type[T], **kwargs: Any) -> T:
        kws = dict(ChainMap(kwargs, self.as_dict()))
        return cls(**kws)
