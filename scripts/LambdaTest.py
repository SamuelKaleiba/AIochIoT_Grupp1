import boto3
from botocore.exceptions import ClientError

def test_lambda_access():
    client = boto3.client('lambda')
    try:
        response = client.list_functions(MaxItems=1)
        print("✓ Lambda: Du har access!")
        for fn in response.get("Functions", []):
            print(f"  - {fn['FunctionName']}")
    except ClientError as e:
        print("✗ Lambda: Ingen access →", e.response['Error']['Message'])

if __name__ == "__main__":
    test_lambda_access()
