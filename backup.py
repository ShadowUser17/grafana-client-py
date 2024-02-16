import os
import sys
import json
import boto3
import tarfile
import pathlib
import grafana
import datetime
import traceback

from urllib import request

# GRAFANA_URL
# GRAFANA_TOKEN
# SLACK_API_URL
# SLACK_CHANNEL
# AWS_S3_BUCKET
# AWS_ENDPOINT_URL
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY


class Backup:
    def __init__(self, client: grafana.Grafana, base_dir: str) -> None:
        self._grafana = client
        self._base_path = pathlib.Path(base_dir)
        self._base_path.mkdir(parents=True, exist_ok=True)

        self._backup_tmpl = r"%Y%m%d%H%M"
        self._folder_data = "data.json"
        self._folder_access = "access.json"

    def backup_all(self) -> None:
        self.backup_folders()
        self.backup_dashboards()
        self.backup_datasources()

    def create_archive(self) -> str:
        '''
        Return path to the archive.
        '''
        time = datetime.datetime.now()
        path = "{}.tgz".format(time.strftime(self._backup_tmpl))
        path = str(self._base_path.joinpath(path))

        with tarfile.open(path, "w:gz") as archive_file:
            for (root, _, files) in os.walk(str(self._base_path)):
                files = filter(lambda item: item.endswith(".json"), files)

                for file_item in files:
                    file_name = os.path.join(root, file_item)
                    archive_file.add(file_name)

        print("Create archive:", path)
        return path

    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    def upload_archive(self, path: str, bucket: str) -> None:
        client = boto3.client("s3")
        file = pathlib.Path(path)
        client.upload_file(str(file), bucket, file.name)
        print("Upload archive: {} to S3 bucket: s3://{}".format(file.name, bucket))

    # https://api.slack.com/reference/surfaces/formatting#building-attachments
    def send_notification(self, api_url: str, channel: str, message: str) -> int:
        if api_url and channel:
            data = json.dumps({
                "username": "grafana-backup-tool", "channel": channel,
                "attachments": [{
                    "title": "Backup data from instance: {}".format(self._grafana._url),
                    "color": "#BDFFC3", "text": message
                }]
            })

            headers = {"Content-type": "application/json"}
            req = request.Request(
                method="POST", url=api_url, headers=headers, data=data.encode()
            )

            with request.urlopen(req) as client:
                return client.status

    def backup_folders(self) -> None:
        for folder_item in self._grafana.list_folders():
            folder_path = self._base_path.joinpath(str(folder_item["id"]))
            folder_path.mkdir(exist_ok=True)
            print("Create folder directory:", folder_path)

            tmp = json.dumps(self._grafana.get_folder_by_uid(folder_item["uid"]))
            folder_data = folder_path.joinpath(self._folder_data)
            folder_data.write_text(tmp)
            print("Store folder data:", folder_data)

            tmp = json.dumps(self._grafana.get_folder_permissions(folder_item["uid"]))
            folder_access = folder_path.joinpath(self._folder_access)
            folder_access.write_text(tmp)
            print("Store folder access:", folder_access)

    def backup_dashboards(self) -> None:
        folder_ids = self._grafana.list_folders()
        folder_ids = map(lambda item: item["id"], folder_ids)

        for dash_item in self._grafana.list_dashboards(folder_ids):
            folder_path = self._base_path.joinpath(str(dash_item["folderId"]))
            folder_path = folder_path.joinpath("dashboards")
            folder_path.mkdir(parents=True, exist_ok=True)

            tmp = json.dumps(self._grafana.get_dashboard_by_uid(dash_item["uid"]))
            dash_file = folder_path.joinpath("{}.json".format(dash_item["title"]))
            dash_file.write_text(tmp)
            print("Store dashboard data:", dash_file)

    def backup_datasources(self) -> None:
        ds_folder = self._base_path.joinpath("datasources")
        ds_folder.mkdir(exist_ok=True)

        for item in self._grafana.list_datasources():
            ds_file = ds_folder.joinpath("{}.json".format(item["name"]))
            ds_file.write_text(json.dumps(item))
            print("Store datasource data:", ds_file)


if __name__ == "__main__":
    try:
        grafana_client = grafana.Grafana(
            url=os.environ.get("GRAFANA_URL", ""),
            token=os.environ.get("GRAFANA_TOKEN", "")
        )

        grafana_backup = Backup(grafana_client, "./data")
        grafana_backup.backup_all()
        archive = grafana_backup.create_archive()
        bucket = os.environ.get("AWS_S3_BUCKET", "")
        grafana_backup.upload_archive(archive, bucket)

        grafana_backup.send_notification(
            api_url=os.environ.get("SLACK_API_URL", ""),
            channel=os.environ.get("SLACK_CHANNEL", ""),
            message="Successfully upload {} to s3://{}/".format(archive, bucket)
        )

    except Exception:
        traceback.print_exc()
        sys.exit(1)
