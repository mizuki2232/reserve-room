# coding=utf-8
import json
import sys
import boto3
import pickle
print 'Loading function'

# todo:check face_id in dynamo.If not registered,guidance with polly
# send registering mail after polly guidance
def lambda_handler(event, context):
    rekognition_client = boto3.client('rekognition')
    s3 = boto3.resource('s3')
    try:
        response = rekognition_client.search_faces_by_image(
            CollectionId='1',
            Image={
                'S3Object': {
                    'Bucket': 'smart-recognition',
                    'Name': 'detect.jpg'
                }
            },
        )
    except Exception as e:
        response = u"顔が写ってないよ！"
        f = open('/tmp/message.txt', 'w')
        f.writelines(response)
        f.close()
        s3.meta.client.upload_file('/tmp/message.txt', 'smart-recognition', 'message.txt')
        sys.exit()
    with open('/tmp/response_txt', 'w') as f:
        pickle.dump(response, f)
    s3.meta.client.upload_file('/tmp/response_txt', 'smart-recognition', 'rekognition-response/result.pickle')
    return response
