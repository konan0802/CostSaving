import requests
import json
import os

from googleapiclient.discovery import build

def list_running_instances(request):
    project_id = os.environ.get('PROJECT_ID')
    # label_filter = os.environ.get('LABEL_FILTER')
    zone = os.environ.get('ZONE')

    instances = []

    gae = build('compute', 'v1')
    gae_list = gae.instances().list(project=project_id, zone=zone).execute()
    for service in gae_list.get('items'):
        if service['status'] == 'RUNNING':
            instances.append(service)

    """
    csql = build('sqladmin', 'v1beta4')
    csql_list = csql.instances().list(project=project_id).execute()
    for instance in csql_list.get('items', []):
        if label_filter is None or label_filter in instance.get('labels', {}):
            instances.append(instance)
    """

    if len(instances) != 0:
        message = "GCPインスタンスが起動中です!!"
        for instance in instances:
            message += "\n・" + instance['name']
        send_line_message(message)

    return 'Completed'

def send_line_message(message):
    channel_token = os.environ.get('CHANNEL_TOKEN')
    user_id = os.environ.get('USER_ID')

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + channel_token
    }
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        print(response.json())
