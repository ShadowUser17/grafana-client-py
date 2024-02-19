import os
import grafana
import unittest


# https://docs.python.org/3/library/unittest.html
class TestGrafanaAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = grafana.Grafana(
            url=os.environ.get("GRAFANA_URL", ""),
            token=os.environ.get("GRAFANA_TOKEN", "")
        )

        data = cls.client.create_folder("test_grafana_folder")
        cls.data_folder_uid = data.get("uid")

        data = {"dashboard": {
            "id": None, "uid": None, "title": "test_grafana_dashboard",
            "timezone": "browser", "schemaVersion": 16, "refresh": "30s"
        }}
        data = cls.client.create_dashboard(data, cls.data_folder_uid)
        cls.data_dashboard_uid = data.get("uid")

        data = {
            "name": "test_grafana_datasource", "type": "loki",
            "access": "proxy", "url": "http://loki.monitoring.svc:3100"
        }
        data = cls.client.create_datasource(data)
        cls.data_datasource_id = data.get("id")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.delete_datasource_by_id(cls.data_datasource_id)
        cls.client.delete_dashboard(cls.data_dashboard_uid)
        cls.client.delete_folder(cls.data_folder_uid)

    def test_list_folders(self) -> None:
        resp = self.client.list_folders()
        self.assertIsNot(resp, list)
        self.assertTrue(resp)

    def test_get_folder(self) -> None:
        resp = self.client.get_folder_by_uid(self.data_folder_uid)
        self.assertIsNot(resp, dict)
        self.assertEqual(resp.get("uid"), self.data_folder_uid)

    def test_folder_permissions(self) -> None:
        resp = self.client.get_folder_permissions(self.data_folder_uid)
        self.assertIsNot(resp, list)
        self.assertTrue(resp)

    def test_update_folder(self) -> None:
        folder_name = "test_grafana_v1"
        resp = self.client.rename_folder(self.data_folder_uid, folder_name)
        self.assertIsNot(resp, dict)
        self.assertEqual(resp.get("title"), folder_name)

    def test_list_dashboards(self) -> None:
        resp = self.client.list_dashboards(folder_ids=[0])
        self.assertIsNot(resp, list)
        self.assertTrue(resp)

    def test_get_dashboard(self) -> None:
        resp = self.client.get_dashboard_by_uid(self.data_dashboard_uid)
        self.assertIsNot(resp, dict)
        data = resp.get("dashboard")
        self.assertEqual(data.get("uid"), self.data_dashboard_uid)

    def test_update_dashboard(self) -> None:
        resp = self.client.get_dashboard_by_uid(self.data_dashboard_uid)
        self.assertIsNot(resp, dict)
        data = resp.get("dashboard")
        self.assertEqual(data.get("uid"), self.data_dashboard_uid)

        dashboard_title = "test_grafana_v1"
        resp["dashboard"]["title"] = dashboard_title
        resp = self.client.update_dashboard(resp)
        self.assertIsNot(resp, dict)

        resp = self.client.get_dashboard_by_uid(self.data_dashboard_uid)
        self.assertIsNot(resp, dict)
        data = resp.get("dashboard")
        self.assertEqual(data.get("title"), dashboard_title)

    def test_list_datasources(self) -> None:
        resp = self.client.list_datasources()
        self.assertIsNot(resp, list)
        self.assertTrue(resp)

    def test_get_datasource(self) -> None:
        resp = self.client.get_datasource_by_id(self.data_datasource_id)
        self.assertIsNot(resp, dict)
        self.assertEqual(resp.get("id"), self.data_datasource_id)

    def test_update_datasource(self) -> None:
        resp = self.client.get_datasource_by_id(self.data_datasource_id)
        self.assertIsNot(resp, dict)
        self.assertEqual(resp.get("id"), self.data_datasource_id)

        data = {"maxLines": 1000, "timeout": 300}
        resp["jsonData"] = data
        resp = self.client.update_datasource_by_id(self.data_datasource_id, resp)
        self.assertIsNot(resp, dict)

        resp = self.client.get_datasource_by_id(self.data_datasource_id)
        self.assertIsNot(resp, dict)
        self.assertEqual(resp.get("id"), self.data_datasource_id)
        self.assertEqual(resp.get("jsonData"), data)


if __name__ == "__main__":
    unittest.main()
