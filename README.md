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
export GRAFANA_TOKEN=''
```
```bash
./env/bin/python3 grafana_test.py -v
```

#### How to use Grafana client:
```python
import grafana

client = grafana.Grafana(grafana_url, grafana_sa_token)
```

#### Tutorials for other tools:
- [backup-tool](docs/Backup.md)
- [restore-scripts](docs/Restore.md)
