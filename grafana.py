import json
import uuid
import urllib3
import logging

from urllib import parse as urllib


class Grafana:
    # https://grafana.com/docs/grafana/latest/developers/http_api/#basic-auth
    def __init__(self, url: str, token: str, verify: bool = False, debug = False) -> None:
        self._url = url
        self.last_status = 0

        if debug:
            logging.getLogger("urllib3").setLevel(logging.DEBUG)

        self._headers = urllib3.HTTPHeaderDict()
        self._headers.add("Accept", "application/json")
        self._headers.add("Content-Type", "application/json")
        self._headers.add("Authorization", "Bearer {}".format(token))

        urllib3.disable_warnings()
        cert_reqs = "CERT_REQUIRED" if verify else "CERT_NONE"
        self._client = urllib3.PoolManager(cert_reqs=cert_reqs)

    def _mkurl(self, path: str) -> str:
        return str(urllib.urljoin(self._url, path))

    def _request(self, method: str, url: str, data: str | bytes = None, ignore_status: int = 0) -> dict:
        try:
            resp = self._client.request(
                method=method, url=url,
                body=data, headers=self._headers
            )
            self.last_status = resp.status
            return resp.json()

        except urllib3.exceptions.HTTPError as error:
            if error.status != ignore_status:
                raise error

            self.last_status = error.status
            return {}

    @property
    def url(self) -> urllib.ParseResult:
        return urllib.urlparse(self._url)

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#get-all-folders
    def list_folders(self) -> list:
        return self._request(
            method="GET", url=self._mkurl("/api/folders")
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#get-folder-by-id
    def get_folder_by_id(self, folder_id: int) -> dict:
        return self._request(
            method="GET", url=self._mkurl("/api/folders/id/{}".format(folder_id)), ignore_status=404
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#get-folder-by-uid
    def get_folder_by_uid(self, uid: str) -> dict:
        return self._request(
            method="GET", url=self._mkurl("/api/folders/{}".format(uid)), ignore_status=404
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder_permissions/#get-permissions-for-a-folder
    def get_folder_permissions(self, uid: str) -> list:
        return self._request(
            method="GET", url=self._mkurl("/api/folders/{}/permissions".format(uid))
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder_permissions/#update-permissions-for-a-folder
    def update_folder_permissions(self, uid: str, data: dict) -> dict:
        return self._request(
            method="POST", url=self._mkurl("/api/folders/{}/permissions".format(uid)), data=json.dumps({"items": data})
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#create-folder
    def create_folder_by_raw(self, data: dict) -> dict:
        return self._request(
            method="POST", url=self._mkurl("/api/folders"), data=json.dumps(data)
        )

    def create_folder(self, name: str, uid: str = None) -> dict:
        uid = uid if uid else str(uuid.uuid1())
        return self.create_folder_by_raw({"uid": uid, "title": name})

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#update-folder
    def update_folder_by_raw(self, uid: str, data: dict) -> dict:
        data["overwrite"] = True

        return self._request(
            method="PUT", url=self._mkurl("/api/folders/{}".format(uid)), data=json.dumps(data)
        )

    def rename_folder(self, uid: str, name: str) -> dict:
        return self.update_folder_by_raw(uid, {"title": name})

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder/#delete-folder
    def delete_folder(self, uid: str) -> dict:
        return self._request(
            method="DELETE", url=self._mkurl("/api/folders/{}".format(uid))
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/folder_dashboard_search/#search-folders-and-dashboards
    def list_dashboards(self, folder_ids: list, page: int = 1, limit: int = 1000) -> list:
        data = urllib.urlencode({
            "type": "dash-db", "limit": limit, "page": page, "folderIds": ",".join(map(str, folder_ids))
        })

        return self._request(
            method="GET", url=self._mkurl("/api/search?{}".format(data))
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/dashboard/#get-dashboard-by-uid
    def get_dashboard_by_uid(self, uid: str) -> dict:
        return self._request(
            method="GET", url=self._mkurl("/api/dashboards/uid/{}".format(uid)), ignore_status=404
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/dashboard/#create--update-dashboard
    def update_dashboard(self, data: dict) -> dict:
        data["overwrite"] = True

        return self._request(
            method="POST", url=self._mkurl("/api/dashboards/db"), data=json.dumps(data)
        )

    def create_dashboard(self, data: dict, folder_uid: str = "") -> dict:
        data["folderUid"] = folder_uid
        data["dashboard"]["id"] = None
        return self.update_dashboard(data)

    # https://grafana.com/docs/grafana/latest/developers/http_api/dashboard/#delete-dashboard-by-uid
    def delete_dashboard(self, uid: str) -> dict:
        return self._request(
            method="DELETE", url=self._mkurl("/api/dashboards/uid/{}".format(uid))
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#get-all-data-sources
    def list_datasources(self) -> list:
        return self._request(
            method="GET", url=self._mkurl("/api/datasources")
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#get-a-single-data-source-by-id
    def get_datasource_by_id(self, ds_id: int) -> dict:
        return self._request(
            method="GET", url=self._mkurl("/api/datasources/{}".format(ds_id))
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#get-a-single-data-source-by-uid
    def get_datasource_by_uid(self, uid: str) -> dict:
        return self._request(
            method="GET", url=self._mkurl("/api/datasources/uid/{}".format(uid)), ignore_status=404
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#get-a-single-data-source-by-name
    def get_datasource_by_name(self, name: str) -> dict:
        return self._request(
            method="GET", url=self._mkurl("/api/datasources/name/{}".format(name)), ignore_status=404
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#create-a-data-source
    def create_datasource(self, data: dict) -> dict:
        return self._request(
            method="POST", url=self._mkurl("/api/datasources"), data=json.dumps(data)
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#update-an-existing-data-source
    def update_datasource(self, uid: str, data: dict) -> dict:
        return self._request(
            method="PUT", url=self._mkurl("/api/datasources/uid/{}".format(uid)), data=json.dumps(data)
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#update-an-existing-data-source-by-id
    def update_datasource_by_id(self, ds_id: int, data: dict) -> dict:
        return self._request(
            method="PUT", url=self._mkurl("/api/datasources/{}".format(ds_id)), data=json.dumps(data)
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#delete-an-existing-data-source-by-id
    def delete_datasource_by_id(self, ds_id: int) -> dict:
        return self._request(
            method="DELETE", url=self._mkurl("/api/datasources/{}".format(ds_id))
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#delete-an-existing-data-source-by-uid
    def delete_datasource_by_uid(self, uid: str) -> dict:
        return self._request(
            method="DELETE", url=self._mkurl("/api/datasources/uid/{}".format(uid))
        )

    # https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#delete-an-existing-data-source-by-name
    def delete_datasource_by_name(self, name: str) -> dict:
        return self._request(
            method="DELETE", url=self._mkurl("/api/datasources/name/{}".format(name))
        )
