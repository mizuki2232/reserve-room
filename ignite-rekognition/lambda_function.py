import json
import boto3
import pickle
print 'Loading function'

# todo:check face_id in dynamo.If not registered,guidance with polly
# send registering mail after polly guidance
def lambda_handler(event, context):
    rekognition_client = boto3.client('rekognition')
    s3 = boto3.resource('s3')
    response = rekognition_client.search_faces_by_image(
        CollectionId='1',
        Image={
            'S3Object': {
                'Bucket': 'smart-recognition',
                'Name': 'detect.jpg'
            }
        },
    )
    with open('/tmp/response_txt', 'w') as f:
        pickle.dump(response, f)
    s3.meta.client.upload_file('/tmp/response_txt', 'smart-recognition', 'rekognition-response/result.pickle')
    return response
