#### Grafana API client on pure Python.
- Official Grafana API reference: [API](https://grafana.com/docs/grafana/latest/developers/http_api/)

#### Implemented functional:
- Folder operations.
- Dashboard operations.
- Datasource operations.

#### Configure environment:
```bash
python3 -m venv --upgrade-deps env && \
./env/bin/pip3 install -r requirements_dev.txt
```

#### Validate project files:
```bash
./env/bin/flake8 --ignore="E501" *.py
```

#### Build docker image:
```bash
docker build -t "shadowuser17/grafana-data-backup:latest" .
```

#### Scan docker image:
```bash
trivy image "shadowuser17/grafana-data-backup:latest"
```

#### Publish docker image:
```bash
docker login -u "${DOCKERHUB_LOGIN}" -p "${DOCKERHUB_TOKEN}"
```
```bash
docker push --all-tags "shadowuser17/grafana-data-backup"
```

#### How to use Grafana client:
```python
import grafana

client = grafana.Grafana(grafana_url, grafana_sa_token)
```

#### How to run Backup tool:
```bash
export AWS_S3_BUCKET="backups"
export GRAFANA_URL="https://grafana.k3s/"
export GRAFANA_TOKEN=""
export AWS_ENDPOINT_URL="http://minio-api.k3s"
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
```
```bash
./env/bin/python3 backup.py
```

#### Manually restore dashboard:
- Remove dashboard metadata:
```bash
python3 -c "from pathlib import Path; from json import (loads,dumps);\
print(dumps(loads(Path(\"${DASH_SRC_FILE}\").read_text())[\"dashboard\"]))" > "${DASH_DST_FILE}"
```
- Go to Grafana: `Home/Dashboards/<folder>`
- Import dashboard from `DASH_DST_FILE`
