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

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#get-folder-by-id
    def get_folder_by_id(self, fid: str) -> dict:
        return self._request(request.Request(
            method="GET", url=self._mkurl("/api/folders/id/{}".format(fid))
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#get-folder-by-uid
    def get_folder_by_uid(self, uid: str) -> dict:
        return self._request(request.Request(
            method="GET", url=self._mkurl("/api/folders/{}".format(uid))
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#create-folder
    def create_folder_by_raw(self, data: dict) -> dict:
        tmp = json.dumps(data)

        return self._request(request.Request(
            method="POST", url=self._mkurl("/api/folders"), data=tmp.encode()
        ))

    def create_folder(self, name: str, uid: str = None) -> dict:
        uid = uid if uid else str(uuid.uuid1())

        return self.create_folder_by_raw({
            "uid": uid, "title": name
        })

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#update-folder
    def update_folder_by_raw(self, uid: str, data: dict) -> dict:
        data["overwrite"] = True
        tmp = json.dumps(data)

        return self._request(request.Request(
            method="PUT", url=self._mkurl("/api/folders/{}".format(uid)), data=tmp.encode()
        ))

    def rename_folder(self, uid: str, name: str) -> dict:
        return self.update_folder_by_raw(uid, {"title": name})

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#delete-folder
    def delete_folder(self, uid: str) -> dict:
        return self._request(request.Request(
            method="DELETE", url=self._mkurl("/api/folders/{}".format(uid))
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder_dashboard_search/#search-folders-and-dashboards
    def list_dashboards(self, folder_ids: list, page: int = 1, limit: int = 1000) -> dict:
        data = urllib.urlencode({
            "type": "dash-db", "limit": limit, "page": page, "folderIds": ",".join(map(str, folder_ids))
        })

        return self._request(request.Request(
            method="GET", url=self._mkurl("/api/search?{}".format(data))
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/dashboard/#get-dashboard-by-uid
    def get_dashboard_by_uid(self, uid: str) -> dict:
        return self._request(request.Request(
            method="GET", url=self._mkurl("/api/dashboards/uid/{}".format(uid))
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/dashboard/#create--update-dashboard
    def modify_dashboard(self, data: dict, folder_uid: str = "") -> dict:
        data["dashboard"]["id"] = None
        data["folderUid"] = folder_uid
        data["overwrite"] = True
        tmp = json.dumps(data)

        return self._request(request.Request(
            method="POST", url=self._mkurl("/api/dashboards/db"), data=tmp.encode()
        ))

    # https://grafana.com/docs/grafana/latest/developers/http_api/dashboard/#delete-dashboard-by-uid
    def delete_dashboard(self, uid: str) -> dict:
        return self._request(request.Request(
            method="DELETE", url=self._mkurl("/api/dashboards/uid/{}".format(uid))
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

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#update-an-existing-data-source
    def update_datasource(self, uid: str, data: dict) -> dict:
        tmp = json.dumps(data)

        return self._request(request.Request(
            method="PUT", url=self._mkurl("/api/datasources/uid/{}".format(uid)), data=tmp.encode()
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
