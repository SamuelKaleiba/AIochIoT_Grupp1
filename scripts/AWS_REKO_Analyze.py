import boto3
from boto3.session import Session

# === Inställningar ===
profile = "axel"
region = "eu-central-1"
bucket_name = "agnesbucket.1"
image_name = "Healthy_vinranka.jpg"
project_version_arn = "arn:aws:rekognition:eu-central-1:390402541367:project/DiseaseDetection1/version/DiseaseDetection1.2025-04-14T11.21.49/1744622509764"

# === Setup AWS-session ===
session = Session(profile_name=profile)
rekognition = session.client("rekognition", region_name=region)

# === Kör analysen ===
response = rekognition.detect_custom_labels(
    ProjectVersionArn=project_version_arn,
    Image={
        'S3Object': {
            'Bucket': bucket_name,
            'Name': image_name
        }
    },
    MinConfidence=70
)

# === Skriv ut resultatet ===
print("\n🧪 Resultat från analys:")
healthy_labels = {"clean", "Disease-free", "frisk", "Uninfected", "Normal", "Unaffected", "välmående", "friska", "healthy"}
powdery_mildew_labels = {"mjoldagg", "vita prickar"}
black_rot_labels = {"svartrot", "svarta prickar"}

healthy_plant = False
powdery_mildew_detected = False
black_rot_detected = False

for label in response['CustomLabels']:
    name = label['Name']
    confidence = label['Confidence']
    print(f" - {name}: {confidence:.2f}%")
    
    if name in healthy_labels and confidence > 90:
        healthy_plant = True
    elif name in powdery_mildew_labels and confidence > 90:
        powdery_mildew_detected = True
    elif name in black_rot_labels and confidence > 90:
        black_rot_detected = True

if healthy_plant:
    print("\n🌱 Detta är en frisk planta!")
elif powdery_mildew_detected:
    print("\n🌿 Plantan är sjuk och har mjöldagg.")
elif black_rot_detected:
    print("\n🌿 Plantan är sjuk och har svartröta.")
else:
    print("\n⚠️ Plantans hälsotillstånd kunde inte fastställas.")
