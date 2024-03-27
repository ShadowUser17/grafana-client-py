#### How to restore folder:
```bash
export FOLDER_PATH="data/85"
export GRAFANA_URL="https://grafana.k3s/"
export GRAFANA_TOKEN=""
```
```bash
./env/bin/python3 restore_folder.py
```

#### How to restore dashboard:
```bash
export DASHBOARD_PATH="data/85/dashboards/c75b0c3f-1240-4d16-beb2-7a78a152269d.json"
export GRAFANA_URL="https://grafana.k3s/"
export GRAFANA_TOKEN=""
```
```bash
./env/bin/python3 restore_dashboard.py
```

#### How to restore datasource:
```bash
export DATASOURCE_PATH="data/datasources/49.json"
export GRAFANA_URL="https://grafana.k3s/"
export GRAFANA_TOKEN=""
```
```bash
./env/bin/python3 restore_datasource.py
```

#### How to manually restore dashboard:
- Remove dashboard metadata:
```bash
python3 -c "from pathlib import Path; from json import (loads,dumps);\
print(dumps(loads(Path(\"${DASH_SRC_FILE}\").read_text())[\"dashboard\"]))" > "${DASH_DST_FILE}"
```
- Go to Grafana: `Home/Dashboards/<folder>`
- Import dashboard from `DASH_DST_FILE`
