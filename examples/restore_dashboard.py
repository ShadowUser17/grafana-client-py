import os
import sys
import json
import grafana
import pathlib
import traceback

# DASHBOARD_PATH
# GRAFANA_URL
# GRAFANA_TOKEN


try:
    dashboard_path = pathlib.Path(os.environ.get("DASHBOARD_PATH"))
    folder_path = dashboard_path.parent.parent.joinpath("data.json")

    grafana_client = grafana.Grafana(
        url=os.environ.get("GRAFANA_URL", ""),
        token=os.environ.get("GRAFANA_TOKEN", "")
    )

    data = json.loads(folder_path.read_text())
    folder_uid = data["uid"]

    data = json.loads(dashboard_path.read_text())
    print(grafana_client.create_dashboard(data, folder_uid))

except Exception:
    traceback.print_exc()
    sys.exit(1)
