import json
import boto3
from receipt import Receipt


def lambda_handler(event, context):
    bucket = "elasticbeanstalk-us-east-2-693859464061"
    document = "receipts/DSC_3607.JPG"
    document = event["path"]
    client = boto3.client('textract')

    # process using S3 object
    response = client.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': document}})

    # Get the text blocks
    # blocks=response['Blocks']
    receipt = Receipt(response)
    receipt.analyze()

    return {
        'statusCode': 200,
        'response': json.dumps(receipt.get_json()),
        # 'body': json.dumps(response)
    }
