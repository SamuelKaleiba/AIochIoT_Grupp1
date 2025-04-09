import boto3
import pyodbc
import os
import time

# AWS Rekognition används fortfarande
rekognition = boto3.client('rekognition')

# Miljövariabler från Lambda
rds_host = os.environ['RDS_HOST']
rds_user = os.environ['RDS_USER']
rds_password = os.environ['RDS_PASSWORD']
rds_db_name = os.environ['RDS_DB_NAME']
rds_port = os.environ.get('RDS_PORT', '1433')

conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={rds_host},{rds_port};'
    f'DATABASE={rds_db_name};'
    f'UID={rds_user};'
    f'PWD={rds_password};'
)

def detect_leaf_disease(bucket, image):
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': image}},
        MaxLabels=10
    )

    labels = [label['Name'] for label in response['Labels']]
    disease = 'Disease' in labels or 'Blight' in labels

    try:
        conn = pyodbc.connect(conn_str, timeout=5)
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
            ','.join(labels),    # Gör om listan till en sträng
            int(disease)         # True/False konverteras till 1/0
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
