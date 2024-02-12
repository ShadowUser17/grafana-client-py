import os
import grafana
import unittest


class TestGrafanaClient(unittest.TestCase):
    def setUp(self) -> None:
        self.grafana_client = grafana.Grafana(
            url=os.environ.get("GRAFANA_URL", ""),
            token=os.environ.get("GRAFANA_TOKEN", "")
        )
