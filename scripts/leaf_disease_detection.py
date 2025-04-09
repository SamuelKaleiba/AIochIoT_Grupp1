import boto3
import time

rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('LeafAnalysisResults')  # Skapa denna tabell i DynamoDB

def detect_leaf_disease(bucket, image):
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': image}},
        MaxLabels=10
    )

    labels = [label['Name'] for label in response['Labels']]
    disease = 'Disease' in labels or 'Blight' in labels

    table.put_item(Item={
        'image': image,
        'timestamp': str(int(time.time())),
        'labels': labels,
        'disease_detected': disease
    })

    return "Sjukdom upptäckt" if disease else "Inga sjukdomar hittade"

def lambda_handler(event, context):
    bucket = event['bucket']
    image = event['image']
    result = detect_leaf_disease(bucket, image)
    return {'statusCode': 200, 'body': result}
