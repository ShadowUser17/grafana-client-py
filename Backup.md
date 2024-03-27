#### How to run Backup tool:
```bash
export DEBUG_MODE=""
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

#### Build docker image:
```bash
docker build -t "shadowuser17/grafana-data-backup:latest" .
```

#### Scan docker image:
```bash
dockle "shadowuser17/grafana-data-backup:latest"
```
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

#### Publish docker image to AWS/ECR:
```bash
export IMAGE_NAME=""
export IMAGE_TAG=""
export AWS_ECR_NAME=""
export AWS_DEFAULT_REGION=""
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
```
```bash
./env/bin/python3 push_aws_ecr.py
```
```bash
docker logout "${AWS_ECR_NAME}"
```

#### How to deploy to K8S:
- For AWS deploy need to create policy and role first!
- Get cronjob from `deploy` and edit.
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
