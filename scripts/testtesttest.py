import boto3
import io
from PIL import Image, ImageDraw, ImageFont
import os

def upload_image_to_s3(bucket, s3_key, local_file_path):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(local_file_path, bucket, s3_key)
        print(f"✓ Bilden '{local_file_path}' laddades upp till s3://{bucket}/{s3_key}")
    except Exception as e:
        print("✗ Fel vid uppladdning till S3:", e)

def display_image(bucket, photo, response):
    s3_connection = boto3.resource('s3')
    s3_object = s3_connection.Object(bucket, photo)
    s3_response = s3_object.get()
    stream = io.BytesIO(s3_response['Body'].read())
    image = Image.open(stream)

    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    for customLabel in response['CustomLabels']:
        print('Label:', customLabel['Name'])
        print('Confidence:', customLabel['Confidence'])
        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']

            try:
                fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 36)
            except:
                fnt = ImageFont.load_default()

            draw.text((left, top), customLabel['Name'], fill='#00d400', font=fnt)

            points = [
                (left, top),
                (left + width, top),
                (left + width, top + height),
                (left, top + height),
                (left, top)
            ]
            draw.line(points, fill='#00d400', width=3)

    image.show()

def analyze_image(model_arn, bucket, s3_key, min_confidence):
    client = boto3.client('rekognition')
    response = client.detect_custom_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': s3_key}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model_arn
    )
    return response

def main():
    # === Ange dina värden här ===
    local_file_path = r'C:\workspace\Iot och AI\AIochIoT_Grupp1\docs\Bilder sjukdomar\test frisk\testfrisk1.jpeg'  # Sökvägen till lokal bild
    bucket = 'agnesbucket.1'
    s3_key = 'sjuk/'
    model_arn = 'arn:aws:rekognition:eu-central-1:390402541367:project/DiseaseDetection1/version/DiseaseDetection1.2025-04-14T11.21.49/1744622509764'
    min_confidence = 95

    # === Steg 1: Ladda upp bilden till S3 ===
    if not os.path.exists(local_file_path):
        print(f"✗ Hittar inte bilden: {local_file_path}")
        return
    upload_image_to_s3(bucket, s3_key, local_file_path)

    # === Steg 2: Analysera bilden ===
    response = analyze_image(model_arn, bucket, s3_key, min_confidence)
    print("✓ Analysen klar! Antal träffar:", len(response['CustomLabels']))

    # === Steg 3: Visa bild med bounding boxes (valfritt) ===
    display_image(bucket, s3_key, response)

if __name__ == "__main__":
    main()