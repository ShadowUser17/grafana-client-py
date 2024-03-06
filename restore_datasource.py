import os
import sys
import json
import grafana
import pathlib
import traceback

# DATASOURCE_PATH
# GRAFANA_URL
# GRAFANA_TOKEN


try:
    datasource_path = pathlib.Path(os.environ.get("DATASOURCE_PATH"))

    grafana_client = grafana.Grafana(
        url=os.environ.get("GRAFANA_URL", ""),
        token=os.environ.get("GRAFANA_TOKEN", "")
    )

    data = json.loads(datasource_path.read_text())
    ds_uid = data["uid"]

    if grafana_client.get_datasource_by_uid(ds_uid):
        print(grafana_client.update_datasource(ds_uid, data))

    else:
        print(grafana_client.create_datasource(data))

except Exception:
    traceback.print_exc()
    sys.exit(1)
