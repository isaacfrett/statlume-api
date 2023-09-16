from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from requests import Request as _Request
from requests import Response, Session
from typing_extensions import Self

from com.dataclasses.mixins import DataClassMixins


class RequestMixins(DataClassMixins):
    def with_url(self, url: str) -> Self:
        return self.as_cls(RequestBuilder, url=url)

    def with_method(self, method: str) -> Self:
        return self.as_cls(RequestBuilder, method=method)

    def with_params(self, params: Dict[str, Any]) -> Self:
        return self.as_cls(RequestBuilder, params=params)

    def with_data(self, data: Dict[str, Any]) -> Self:
        return self.as_cls(RequestBuilder, data=data)

    def with_headers(self, headers: Dict[str, Any]) -> Self:
        return self.as_cls(RequestBuilder, headers=headers)

    def with_json(self, json: Dict[str, Any]) -> Self:
        return self.as_cls(RequestBuilder, json=json)

    def as_request(self) -> Request:
        return self.as_cls(Request)


@dataclass(frozen=True)
class RequestBuilder(RequestMixins):
    url: Optional[str] = None
    method: Optional[str] = "GET"
    params: Optional[Dict[str, Any]] = field(default_factory=dict)
    data: Optional[Dict[str, Any]] = field(default_factory=dict)
    headers: Optional[Dict[str, Any]] = field(default_factory=dict)
    json: Optional[Dict[str, Any]] = field(default_factory=dict)


class Request(_Request):
    def send(self, session: Session) -> Response:
        with session as ses:
            preq = ses.prepare_request(self)
            res = ses.send(preq)
            return res
