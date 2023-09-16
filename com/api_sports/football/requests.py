import os

from requests import Response, Session

from com.http.requests import RequestBuilder

request_builder = RequestBuilder()
session = Session()


def get_account_status(session: Session) -> Response:
    url = "https://v1.american-football.api-sports.io/status"
    return (
        request_builder.with_url(url=url)
        .with_headers({"x-apisports-key": os.environ.get("APISPORTS")})
        .as_request()
        .send(session)
    )


print(get_account_status(session=session).status_code)
