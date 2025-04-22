import boto3

# --- Hårdkodad AWS-behörighet ---
AWS_ACCESS_KEY_ID = 'AKIAVVZOOA436CCNPEPQ'
AWS_SECRET_ACCESS_KEY = 'XxXxXxXxXxXxXxXxXxXxXxXxXxXx'  # Använd en säker metod för att hantera hemligheter i produktion
AWS_REGION = 'eu-central-1'

# --- AWS Rekognition-klient ---
rekognition = boto3.client(
    'rekognition',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# --- AWS Lex V2-klient ---
lex_v2 = boto3.client(
    'lexv2-runtime',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# --- Lex V2 Metadata ---
LEX_BOT_ID = "VAN9BJTZBH"
LEX_BOT_ALIAS_ID = "RTHXTBTLOH"
LEX_LOCALE_ID = "en_US"  # eller "en_US" om du valt engelska i botten

# --- Funktion för att analysera bild via Rekognition Custom Labels ---
def analyze_image(s3_key, bucket_name, access_key, secret_key, region, model_arn):
    client = boto3.client(
        'rekognition',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    response = client.detect_custom_labels(
        ProjectVersionArn=model_arn,
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': s3_key
            }
        },
        MaxResults=10,
        MinConfidence=70
    )

    labels = [label["Name"] for label in response["CustomLabels"]]
    return labels