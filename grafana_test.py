import os
import time
import grafana
import unittest


class TestGrafanaAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = grafana.Grafana(
            url=os.environ.get("GRAFANA_URL", ""),
            token=os.environ.get("GRAFANA_TOKEN", "")
        )

    def test_folder_functions(self) -> None:
        resp = self.client.list_folders()
        print("list_folders:")
        for item in resp:
            print("\t{}: ({}, {})".format(item.get("title"), item.get("id"), item.get("uid")))

        time.sleep(1.0)
        resp = self.client.create_folder("test_grafana_api_v1")
        folder_id = resp.get("id")
        folder_uid = resp.get("uid")
        print("create_folder: ({}, {})".format(folder_id, folder_uid))

        time.sleep(1.0)
        resp = self.client.rename_folder(folder_uid, "test_grafana_api_v2")
        print("rename_folder: ({}, {})".format(resp.get("id"), resp.get("title")))

        time.sleep(1.0)
        resp = self.client.get_folder_by_id(folder_id)
        print("get_folder_by_id: ({}, {})".format(resp.get("id"), resp.get("title")))

        time.sleep(1.0)
        resp = self.client.get_folder_by_uid(folder_uid)
        print("get_folder_by_uid: ({}, {})".format(resp.get("uid"), resp.get("title")))

        time.sleep(1.0)
        resp = self.client.get_folder_permissions(folder_uid)
        print("get_folder_permissions:")
        for item in resp:
            print("\t{}: {}/{}: {}".format(item.get("title"), item.get("teamId"), item.get("userId"), item.get("role")))

        time.sleep(1.0)
        resp = self.client.delete_folder(folder_uid)
        print("delete_folder: {}".format(resp))

    def test_datasource_functions(self) -> None:
        resp = self.client.list_datasources()
        print("list_datasources:")
        for item in resp:
            print("\t{}: {} RO: {}".format(item.get("id"), item.get("name"), item.get("readOnly")))

        time.sleep(1.0)
        resp = self.client.create_datasource({
            "name": "test_grafana_api", "type": "loki",
            "access": "proxy", "url": "http://loki.monitoring.svc:3100"
        })

        ds_id = resp.get("id")
        ds_uid = resp.get("uid")
        print("create_datasource: ({}, {})".format(ds_id, ds_uid))

        time.sleep(1.0)
        resp = self.client.get_datasource_by_id(ds_id)
        print("get_datasource_by_id: ({}, {})".format(resp.get("id"), resp.get("name")))

        time.sleep(1.0)
        resp["jsonData"] = {"maxLines": 1000, "timeout": 300}
        self.client.update_datasource_by_id(ds_id, resp)
        resp = self.client.get_datasource_by_id(ds_id)
        print("update_datasource_by_id: {}".format(resp.get("jsonData")))

        time.sleep(1.0)
        resp = self.client.delete_datasource_by_id(ds_id)
        print("delete_datasource_by_id: {}".format(resp))

    def test_dashboard_functions(self) -> None:
        resp = self.client.create_folder("test_grafana_dashboards")
        folder_uid = resp.get("uid")
        print("create_folder: ({}, {})".format(folder_uid, resp.get("title")))

        time.sleep(1.0)
        data = {"dashboard": {
            "id": None, "uid": None,
            "title": "testing_dashboard",
            "timezone": "browser",
            "schemaVersion": 16,
            "refresh": "30s"
        }}
        resp = self.client.create_dashboard(data, folder_uid)
        dashboard_uid = resp.get("uid")
        print("create_dashboard: ({}, {})".format(resp.get("id"), resp.get("slug")))

        time.sleep(1.0)
        resp = self.client.get_dashboard_by_uid(dashboard_uid)
        data = resp.get("dashboard")
        print("get_dashboard_by_uid: ({}, {})".format(data.get("id"), data.get("version")))

        time.sleep(1.0)
        data = resp
        data["dashboard"]["title"] = "testing_dashboard_v2"
        resp = self.client.update_dashboard(data)
        print("update_dashboard: ({}, {})".format(resp.get("id"), resp.get("slug")))

        time.sleep(1.0)
        resp = self.client.get_dashboard_by_uid(dashboard_uid)
        data = resp.get("dashboard")
        print("get_dashboard_by_uid: ({}, {})".format(data.get("id"), data.get("version")))

        time.sleep(1.0)
        resp = self.client.delete_dashboard(dashboard_uid)
        print("delete_dashboard: {}".format(resp))

        time.sleep(1.0)
        resp = self.client.delete_folder(folder_uid)
        print("delete_folder: {}".format(resp))


if __name__ == "__main__":
    unittest.main()
