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

#### Scan project dependencies:
```bash
./env/bin/pip-audit -f json | python3 -m json.tool
```

#### Validate project files:
```bash
./env/bin/flake8 --ignore="E501" *.py
```

#### Run unit tests:
```bash
./env/bin/python3 grafana_test.py -v
```

#### Build docker image:
```bash
docker build -t "shadowuser17/grafana-data-backup:latest" .
```

#### Scan docker image:
```bash
trivy image "shadowuser17/grafana-data-backup:latest"
```
```bash
trivy image -f json -o report.json --list-all-pkgs "shadowuser17/grafana-data-backup:latest"
```

#### Publish docker image:
```bash
docker login -u "${DOCKERHUB_LOGIN}" -p "${DOCKERHUB_TOKEN}"
```
```bash
docker push --all-tags "shadowuser17/grafana-data-backup"
```

#### How to deploy to K8S:
- For AWS deploy need to create policy and role first!
- Get cronjob from `examples` and edit.
- Apply the edited file from `kubectl` command.

#### Change cronjob schedule time:
```bash
kubectl -n testing patch cronjob grafana-backup -p '{"spec": {"schedule": "*/5 * * * *"}}'
```

#### Disable cronjob manually:
```bash
kubectl -n testing patch cronjob grafana-backup -p '{"spec": {"suspend": true}}'
```

#### Delete jobs generated from cronjob:
```bash
kubectl -n testing delete jobs -l "app=grafana-backup"
```

#### How to use Grafana client:
```python
import grafana

client = grafana.Grafana(grafana_url, grafana_sa_token)
```

#### How to run Backup tool:
```bash
export GRAFANA_URL="https://grafana.k3s/"
export GRAFANA_TOKEN=""
export SLACK_API_URL=""
export SLACK_CHANNEL=""
export AWS_ENDPOINT_URL="http://minio-api.k3s"
export AWS_S3_BUCKET="backups"
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
