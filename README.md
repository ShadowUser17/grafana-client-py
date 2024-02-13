#### Grafana API client on pure Python.
- Official Grafana API reference: [API](https://grafana.com/docs/grafana/latest/developers/http_api/)

#### Implemented functional:
- Folder operations.
- Dashboard operations.
- Datasource operations.

#### Configure environment:
```bash
python3 -m venv --upgrade-deps env && \
./env/bin/pip3 install -r requirements.txt
```

#### How to use Grafana client:
```python
import grafana

client = grafana.Grafana(grafana_url, grafana_sa_token)
```

#### Manually restore dashboard:
- Remove dashboard metadata:
```bash
python3 -c "from pathlib import Path; from json import (loads,dumps);\
print(dumps(loads(Path(\"${DASH_SRC_FILE}\").read_text())[\"dashboard\"]))" > "${DASH_DST_FILE}"
```
- Go to Grafana: `Home/Dashboards/<folder>`
- Import dashboard from `DASH_DST_FILE`
