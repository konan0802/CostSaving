import boto3
import os

# SESとEC2クライアントを作成
ses = boto3.client('ses')
ec2 = boto3.resource('ec2')

# 環境変数からメールアドレスを取得
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
SENDER_EMAIL_ADDRESS = os.getenv('SENDER_EMAIL_ADDRESS')

def lambda_handler(event, context):
    running_instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    for instance in running_instances:
        instance_name = ''
        is_cost_saving = False
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                instance_name = tag['Value']
            if tag['Key'] == 'CostSaving':
                is_cost_saving = True
            if instance_name and is_cost_saving:
                send_email(instance_name)
                break

def send_email(instance_name):
    ses.send_email(
        Source=SENDER_EMAIL_ADDRESS,
        Destination={
            'ToAddresses': [
                EMAIL_ADDRESS,
            ],
        },
        Message={
            'Subject': {
                'Data': 'コスト削減EC2が稼働中！！',
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': f'EC2インスタンス［{instance_name}］が現在稼働しています！！',
                    'Charset': 'UTF-8'
                },
            },
        }
    )

