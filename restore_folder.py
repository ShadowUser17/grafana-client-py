import os
import sys
import json
import pathlib
import grafana
import traceback

# FOLDER_PATH
# GRAFANA_URL
# GRAFANA_TOKEN


try:
    folder_base = pathlib.Path(os.environ.get("FOLDER_PATH"))
    folder_data = folder_base.joinpath("data.json")
    folder_access = folder_base.joinpath("access.json")

    grafana_client = grafana.Grafana(
        url=os.environ.get("GRAFANA_URL", ""),
        token=os.environ.get("GRAFANA_TOKEN", "")
    )

    data = json.loads(folder_data.read_text())
    folder_uid = data["uid"]

    if grafana_client.get_folder_by_uid(folder_uid):
        print(grafana_client.update_folder_by_raw(folder_uid, data))

    else:
        print(grafana_client.create_folder_by_raw(data))

    data = json.loads(folder_access.read_text())
    print(grafana_client.update_folder_permissions(folder_uid, data))

except Exception:
    traceback.print_exc()
    sys.exit(1)
