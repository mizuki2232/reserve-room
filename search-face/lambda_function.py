# coding=utf-8

import json
import boto3
import pickle
from boto3.dynamodb.conditions import Key, Attr
import sys

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('rekognition')
print 'Loading function'


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    with open('/tmp/obj', 'wb') as data:
        s3.download_fileobj('your_bucket_name', 'result_pickle', data)
    with open('/tmp/obj', 'r') as f:
        rekognition_result  = pickle.load(f)
    try:
        face_id = rekognition_result['FaceMatches'][0]['Face']['FaceId']
        Confidence = rekognition_result['FaceMatches'][0]['Face']['Confidence']
    except Exception as e:
        print (e)
    if Confidence < 70:
        message = u'知らない顔！パオパオ'
        message = message.encode('utf-8')
        f = open('/tmp/message.txt', 'w')
        f.writelines(message)
        f.close()
        # messageをS3にpost
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file('/tmp/message.txt', 'your_bucket_name', 'message.txt')
        sys.exit()
        

    try:
        response = table.get_item(
            Key={
                'face_id': face_id
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    slack_name = response['Item']['slack_name']
    with open('/tmp/slack_name_dump', 'w') as f:
        pickle.dump(slack_name, f)
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file('/tmp/slack_name_dump', 'your_bucket_name', 'slack_name')
    return response
