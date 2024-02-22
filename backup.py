import os
import sys
import json
import boto3
import tarfile
import pathlib
import logging
import grafana
import datetime
import traceback

from urllib import request

# DEBUG_MODE
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
        self._backup_items = []
        self._backup_items_file = "items.txt"
        self._backup_tmpl = r"%Y%m%d%H%M"
        self._folder_data = "data.json"
        self._folder_access = "access.json"

    def backup_all(self) -> None:
        self.backup_folders()
        self.backup_dashboards()
        self.backup_datasources()
        self.create_item_list()

    def update_item_list(self, name: str, file: str) -> None:
        self._backup_items.append("\"{}\": {}".format(name, file))

    def create_item_list(self) -> None:
        path = self._base_path.joinpath(self._backup_items_file)

        logging.info("Store backup items: {}".format(path))
        data = "\n".join(self._backup_items)
        path.write_text(data)

    def create_archive(self) -> str:
        '''
        Return path to the archive.
        '''
        time = datetime.datetime.now()
        path = "{}.tgz".format(time.strftime(self._backup_tmpl))
        path = str(self._base_path.joinpath(path))

        logging.debug("Open archive: {}".format(path))
        with tarfile.open(path, "w:gz") as archive_file:
            for (root, _, files) in os.walk(str(self._base_path)):
                files = filter(lambda item: not item.endswith(".tgz"), files)

                for file_item in files:
                    file_name = os.path.join(root, file_item)
                    archive_file.add(file_name)

        logging.info("Created archive: {}".format(path))
        return path

    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    def upload_archive(self, path: str, bucket: str) -> None:
        client = boto3.client("s3")
        file = pathlib.Path(path)
        client.upload_file(str(file), bucket, file.name)
        logging.info("Upload archive: {} to S3 bucket: s3://{}".format(file.name, bucket))

    # https://api.slack.com/reference/surfaces/formatting#building-attachments
    def send_notification(self, api_url: str, channel: str, message: str, is_failed: bool = False) -> int:
        color = "#FF9FA1" if is_failed else "#BDFFC3"

        if api_url and channel:
            data = json.dumps({
                "username": "grafana-backup-tool", "channel": channel,
                "icon_url": "https://grafana.com/img/fav32.png",
                "attachments": [{
                    "title": "Backup data from instance: {}".format(self._grafana.url.geturl()),
                    "color": color, "text": message
                }]
            })

            headers = {"Content-type": "application/json"}
            req = request.Request(
                method="POST", url=api_url, headers=headers, data=data.encode()
            )

            with request.urlopen(req) as client:
                return client.status

    def backup_folders(self) -> None:
        logging.debug("Create directory: {}".format(self._base_path))
        self._base_path.mkdir(parents=True, exist_ok=True)

        logging.debug("Run list_folders()")
        for folder_item in self._grafana.list_folders():
            logging.debug("Current item: {}".format(folder_item))

            folder_path = self._base_path.joinpath(str(folder_item["id"]))
            self.update_item_list(folder_item["title"], folder_path)

            logging.info("Create directory: {}".format(folder_path))
            folder_path.mkdir(exist_ok=True)

            logging.debug("Run get_folder_by_uid({})".format(folder_item["uid"]))
            tmp = json.dumps(self._grafana.get_folder_by_uid(folder_item["uid"]))

            folder_data = folder_path.joinpath(self._folder_data)
            logging.info("Store folder data: {}".format(folder_data))
            folder_data.write_text(tmp)

            logging.debug("Run get_folder_permissions({})".format(folder_item["uid"]))
            tmp = json.dumps(self._grafana.get_folder_permissions(folder_item["uid"]))

            folder_access = folder_path.joinpath(self._folder_access)
            logging.info("Store folder access: {}".format(folder_access))
            folder_access.write_text(tmp)

    def backup_dashboards(self) -> None:
        logging.debug("Run list_folders()")
        folder_ids = self._grafana.list_folders()
        folder_ids = list(map(lambda item: item["id"], folder_ids))

        logging.debug("Run list_dashboards({})".format(folder_ids))
        for dash_item in self._grafana.list_dashboards(folder_ids):
            logging.debug("Current item: {}".format(dash_item))

            dash_folder_id = dash_item.get("folderId", 0)
            logging.debug("Get folder id: {}".format(dash_folder_id))

            if dash_folder_id:
                folder_path = self._base_path.joinpath(str(dash_folder_id))
                folder_path = folder_path.joinpath("dashboards")
                folder_path.mkdir(parents=True, exist_ok=True)

                logging.debug("Run get_dashboard_by_uid({})".format(dash_item["uid"]))
                tmp = json.dumps(self._grafana.get_dashboard_by_uid(dash_item["uid"]))

                dash_file = folder_path.joinpath("{}.json".format(dash_item["uid"]))
                logging.info("Store dashboard data: {}".format(dash_file))
                self.update_item_list(dash_item["title"], dash_file)
                dash_file.write_text(tmp)

    def backup_datasources(self) -> None:
        ds_folder = self._base_path.joinpath("datasources")
        logging.info("Create directory: {}".format(ds_folder))
        ds_folder.mkdir(parents=True, exist_ok=True)

        logging.debug("Run list_datasources()")
        for item in self._grafana.list_datasources():
            logging.debug("Current item: {}".format(item))

            ds_file = ds_folder.joinpath("{}.json".format(item["id"]))
            self.update_item_list(item["name"], ds_file)

            logging.info("Store datasource data: {}".format(ds_file))
            ds_file.write_text(json.dumps(item))


if __name__ == "__main__":
    log_level = logging.DEBUG if os.environ.get("DEBUG_MODE", "") else logging.INFO
    logging.basicConfig(
        format=r'%(levelname)s [%(asctime)s]: "%(message)s"',
        datefmt=r'%Y-%m-%d %H:%M:%S', level=log_level
    )

    grafana_client = grafana.Grafana(
        url=os.environ.get("GRAFANA_URL", ""),
        token=os.environ.get("GRAFANA_TOKEN", "")
    )

    grafana_backup = Backup(grafana_client, "./data")
    try:
        grafana_backup.backup_all()
        archive = grafana_backup.create_archive()
        bucket = os.environ.get("AWS_S3_BUCKET", "")
        grafana_backup.upload_archive(archive, bucket)

        grafana_backup.send_notification(
            api_url=os.environ.get("SLACK_API_URL", ""),
            channel=os.environ.get("SLACK_CHANNEL", ""),
            message="Successfully upload {} to s3://{}/".format(archive, bucket)
        )

    except Exception as error:
        logging.error(traceback.format_exc())

        message = "Failure: ({}: {})".format(error.__class__.__name__, error)
        grafana_backup.send_notification(
            api_url=os.environ.get("SLACK_API_URL", ""),
            channel=os.environ.get("SLACK_CHANNEL", ""),
            message=message, is_failed=True
        )
        sys.exit(1)
