#Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)

import boto3
from botocore.config import Config
from botocore.exceptions import NoCredentialsError

def start_model(project_arn, model_arn, version_name, min_inference_units):

    # Use SSO profile for boto3 session
    try:
        session = boto3.Session(profile_name='axel')
        client = session.client('rekognition', config=Config(region_name='eu-central-1'))
    except NoCredentialsError as e:
        print("AWS credentials not found. Ensure your SSO profile is configured correctly.")
        print(e)
        return

    try:
        # Start the model
        print('Starting model: ' + model_arn)
        response = client.start_project_version(ProjectVersionArn=model_arn, MinInferenceUnits=min_inference_units)
        # Wait for the model to be in the running state
        project_version_running_waiter = client.get_waiter('project_version_running')
        project_version_running_waiter.wait(ProjectArn=project_arn, VersionNames=[version_name])

        # Get the running status
        describe_response = client.describe_project_versions(ProjectArn=project_arn,
                                                             VersionNames=[version_name])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage'])
    except Exception as e:
        print(e)

    print('Done...')

def main():
    project_arn = 'arn:aws:rekognition:eu-central-1:390402541367:project/DiseaseDetection1/1744621659141'
    model_arn = 'arn:aws:rekognition:eu-central-1:390402541367:project/DiseaseDetection1/version/DiseaseDetection1.2025-04-14T11.21.49/1744622509764'
    min_inference_units = 1
    version_name = 'DiseaseDetection1.2025-04-14T11.21.49'
    start_model(project_arn, model_arn, version_name, min_inference_units)

if __name__ == "__main__":
    main()