import ssl
import json
import uuid

from urllib import request
from urllib import parse as urllib


class Grafana:
    # https://grafana.com/docs/grafana/latest/developers/http_api/#basic-auth
    def __init__(self, url: str, token: str, verify: bool = False) -> None:
        self._url = url
        self._verify = verify
        self._headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token)
        }

    def _mkurl(self, path: str) -> str:
        return str(urllib.urljoin(self._url, path))

    def _request(self, req: request.Request) -> dict:
        req.headers = self._headers
        ctx = None if self._verify else ssl._create_unverified_context()

        with request.urlopen(url=req, context=ctx) as client:
            return json.loads(client.read())

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#get-all-folders
    def list_folders(self) -> dict:
        return self._request(request.Request(
            method="GET", url=self._mkurl("/api/folders")
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#create-folder
    def create_folder(self, name: str) -> dict:
        data = json.dumps({
            "uid": str(uuid.uuid1()), "title": name
        })

        return self._request(request.Request(
            method="POST", url=self._mkurl("/api/folders"), data=data.encode()
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#delete-folder
    def delete_folder(self, uid: str) -> dict:
        return self._request(request.Request(
            method="DELETE", url=self._mkurl("/api/folders/{}".format(uid))
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#get-all-data-sources
    def list_datasources(self) -> dict:
        return self._request(request.Request(
            method="GET", url=self._mkurl("/api/datasources")
        ))