import os
import base64
import json
import requests

from google.cloud import secretmanager
from googleapiclient import discovery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_notification(event, context):
    # イベントデータをデコード
    data = base64.b64decode(event['data']).decode('utf-8')
    payload = json.loads(data)
    
    # イベントデータからラベルを取得
    label = payload['label']
    
    # Cloud SQLインスタンスが実行中かどうかを確認
    if label == 'cloud-sql-instance':
        instance_name = payload['instance_name']
        project_id = payload['project_id']
        zone = payload['zone']
        
        credentials, _ = google.auth.default()
        service = discovery.build('sqladmin', 'v1beta4', credentials=credentials)
        request = service.instances().get(project=project_id, instance=instance_name, zone=zone)
        response = request.execute()
        instance_state = response['state']
        
        # インスタンスが実行中の場合は通知を送信
        if instance_state == 'RUNNABLE':
            send_email_notification()
    
    # GCEインスタンスが実行中かどうかを確認
    if label == 'gce-instance':
        instance_name = payload['instance_name']
        project_id = payload['project_id']
        zone = payload['zone']
        
        credentials, _ = google.auth.default()
        compute = discovery.build('compute', 'v1', credentials=credentials)
        request = compute.instances().get(project=project_id, zone=zone, instance=instance_name)
        response = request.execute()
        instance_status = response['status']
        
        # インスタンスが実行中の場合は通知を送信
        if instance_status == 'RUNNING':
            send_email_notification()

def send_email_notification():
    # SendGridのAPIキーを取得
    secret_name = 'sendgrid-api-key'
    project_id = os.environ.get('GCP_PROJECT')
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    api_key = response.payload.data.decode('UTF-8')
    
    # メールの送信設定
    message = Mail(
        from_email='sender@example.com',
        to_emails='recipient@example.com',
        subject='Instance Notification',
        plain_text_content='The labeled instance is running.'
    )
    
    try:
        # SendGridでメールを送信
        sendgrid_client = SendGridAPIClient(api_key=api_key)
        response = sendgrid_client.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))
