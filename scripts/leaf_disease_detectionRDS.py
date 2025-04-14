import boto3
from db_connection import get_connection
from db_init import ensure_leaf_table_exists
import time

rekognition = boto3.client('rekognition')

def detect_leaf_disease(bucket, image):
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': image}},
        MaxLabels=10
    )

    labels = [label['Name'] for label in response['Labels']]
    disease = 'Disease' in labels or 'Blight' in labels

    try:
        conn = get_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO LeafAnalysisResults (
                image, timestamp, labels, disease_detected
            )
            VALUES (?, ?, ?, ?)
        """

        cursor.execute(insert_query, (
            image,
            int(time.time()),
            ','.join(labels),
            int(disease)
        ))

        conn.commit()

    except Exception as e:
        return f"Fel vid SQL: {str(e)}"

    finally:
        conn.close()

    return "Sjukdom upptäckt" if disease else "Inga sjukdomar hittade"

def lambda_handler(event, context):
    bucket = event['bucket']
    image = event['image']
    result = detect_leaf_disease(bucket, image)
    return {'statusCode': 200, 'body': result}
