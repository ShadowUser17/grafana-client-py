import os
import time
import grafana


def test_folder_functions(client: grafana.Grafana) -> None:
    resp = client.list_folders()
    print("list_folders:")
    for item in resp:
        print("\t{}: ({}, {})".format(item.get("title"), item.get("id"), item.get("uid")))

    time.sleep(1.0)
    resp = client.create_folder("test_grafana_api_v1")
    folder_id = resp.get("id")
    folder_uid = resp.get("uid")
    print("create_folder: ({}, {})".format(folder_id, folder_uid))

    time.sleep(1.0)
    resp = client.rename_folder(folder_uid, "test_grafana_api_v2")
    print("rename_folder: ({}, {})".format(resp.get("id"), resp.get("title")))

    time.sleep(1.0)
    resp = client.get_folder_by_id(folder_id)
    print("get_folder_by_id: ({}, {})".format(resp.get("id"), resp.get("title")))

    time.sleep(1.0)
    resp = client.get_folder_by_uid(folder_uid)
    print("get_folder_by_uid: ({}, {})".format(resp.get("uid"), resp.get("title")))

    time.sleep(1.0)
    resp = client.get_folder_permissions(folder_uid)
    print("get_folder_permissions:")
    for item in resp:
        print("\t{}: {}/{}: {}".format(item.get("title"), item.get("teamId"), item.get("userId"), item.get("role")))

    time.sleep(1.0)
    resp = client.delete_folder(folder_uid)
    print("delete_folder: {}".format(resp))


def test_datasource_functions(client: grafana.Grafana) -> None:
    resp = client.list_datasources()
    print("list_datasources:")
    for item in resp:
        print("\t{}: {} RO: {}".format(item.get("id"), item.get("name"), item.get("readOnly")))

    time.sleep(1.0)
    resp = client.create_datasource({
        "name": "test_grafana_api", "type": "loki",
        "access": "proxy", "url": "http://loki.monitoring.svc:3100"
    })

    ds_id = resp.get("id")
    ds_uid = resp.get("uid")
    print("create_datasource: ({}, {})".format(ds_id, ds_uid))

    time.sleep(1.0)
    resp = client.get_datasource_by_id(ds_id)
    print("get_datasource_by_id: ({}, {})".format(resp.get("id"), resp.get("name")))

    time.sleep(1.0)
    resp["jsonData"] = {"maxLines": 1000, "timeout": 300}
    client.update_datasource_by_id(ds_id, resp)
    resp = client.get_datasource_by_id(ds_id)
    print("update_datasource_by_id: {}".format(resp.get("jsonData")))

    time.sleep(1.0)
    resp = client.delete_datasource_by_id(ds_id)
    print("delete_datasource_by_id: {}".format(resp))


try:
    client = grafana.Grafana(
        url=os.environ.get("GRAFANA_URL", ""),
        token=os.environ.get("GRAFANA_TOKEN", "")
    )
    test_folder_functions(client)

except Exception as error:
    print("Error: {}, Message: {}".format(error.__class__.__name__, error))
