import json
import pathlib
import grafana
import traceback


class Backup:
    def __init__(self, client: grafana.Grafana, base_dir: str) -> None:
        self._grafana = client
        self._base_path = pathlib.Path(base_dir)
        self._base_path.mkdir(parents=True, exist_ok=True)

        self._folder_data = "data.json"
        self._folder_access = "access.json"

    def backup_folders(self) -> None:
        for folder_item in self._grafana.list_folders():
            try:
                folder_path = self._base_path.joinpath(str(folder_item["id"]))
                folder_path.mkdir(exist_ok=True)
                print("Create folder directory:", folder_path)

                # Store folder object in data.json
                tmp = json.dumps(self._grafana.get_folder_by_uid(folder_item["uid"]))
                folder_data = folder_path.joinpath(self._folder_data)
                folder_data.write_text(tmp)
                print("Store folder data:", folder_data)

                # Store folder permissions to access.json
                tmp = json.dumps(self._grafana.get_folder_permissions(folder_item["uid"]))
                folder_access = folder_path.joinpath(self._folder_access)
                folder_access.write_text(tmp)
                print("Store folder access:", folder_access)

            except Exception:
                traceback.print_exc()

    def backup_dashboards(self) -> None:
        pass

    def backup_batasources(self) -> None:
        pass
