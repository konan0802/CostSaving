import os
from googleapiclient.discovery import build

def list_running_instances(request):
    project_id = os.environ.get('PROJECT_ID')
    label_filter = os.environ.get('LABEL_FILTER')

    service = build('appengine', 'v1')
    response = service.apps().services().list(
        appsId=project_id,
        pageSize=100  # 必要に応じてページサイズを調整
    ).execute()

    instances = []
    for service in response.get('services', []):
        if service.get('split', {}).get('allocations', []):
            for instance in service['split']['allocations']:
                if label_filter is None or label_filter in instance.get('labels', {}):
                    instances.append(instance)

    sql_service = build('sqladmin', 'v1beta4')
    instances_list = sql_service.instances().list(project=project_id).execute()
    for instance in instances_list.get('items', []):
        if label_filter is None or label_filter in instance.get('labels', {}):
            instances.append(instance)

    for instance in instances:
        print(f"Instance ID: {instance['instance']}")

    return 'Completed'
