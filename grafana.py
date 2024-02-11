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

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#get-folder-by-uid
    def get_folder_by_uid(self, uid: str) -> dict:
        return self._request(request.Request(
            method="GET", url=self._mkurl("/api/folders/{}".format(uid))
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#create-folder
    def create_folder(self, name: str, uid: str = None) -> dict:
        uid = uid if uid else str(uuid.uuid1())

        data = json.dumps({
            "uid": uid, "title": name
        })

        return self._request(request.Request(
            method="POST", url=self._mkurl("/api/folders"), data=data.encode()
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#update-folder
    def update_folder(self, uid: str, name: str, version: int) -> dict:
        data = json.dumps({
            "title": name, "version": version
        })

        return self._request(request.Request(
            method="PUT", url=self._mkurl("/api/folders/{}".format(uid)), data=data.encode()
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

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#get-a-single-data-source-by-uid
    def get_datasource_by_uid(self, uid: str) -> dict:
        return self._request(request.Request(
            method="GET", url=self._mkurl("/api/datasources/uid/{}".format(uid))
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#get-a-single-data-source-by-name
    def get_datasource_by_name(self, name: str) -> dict:
        return self._request(request.Request(
            method="GET", url=self._mkurl("/api/datasources/name/{}".format(name))
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#create-a-data-source
    def create_datasource(self, data: dict) -> dict:
        tmp = json.dumps(data)

        return self._request(request.Request(
            method="POST", url=self._mkurl("/api/datasources"), data=tmp.encode()
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#delete-an-existing-data-source-by-uid
    def delete_datasource_by_uid(self, uid: str) -> dict:
        return self._request(request.Request(
            method="DELETE", url=self._mkurl("/api/datasources/uid/{}".format(uid))
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#delete-an-existing-data-source-by-name
    def delete_datasource_by_name(self, name: str) -> dict:
        return self._request(request.Request(
            method="DELETE", url=self._mkurl("/api/datasources/name/{}".format(name))
        ))
