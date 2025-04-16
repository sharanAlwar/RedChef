import boto3
import json

def test_bedrock_access():
    try:
        # Initialize AWS clients with hardcoded credentials
        aws_config = {
            'region_name': 'us-east-1',  # Primary region
            'aws_access_key_id': '',  # Replace with your actual access key
            'aws_secret_access_key': ''  # Replace with your actual secret key
        }

        # Test EC2 access
        print("\nTesting EC2 access...")
        ec2 = boto3.client('ec2', **aws_config)
        response = ec2.describe_instances()
        
        print("\nEC2 Instances:")
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                print(f"- Instance ID: {instance['InstanceId']}")
                print(f"  State: {instance['State']['Name']}")
                print(f"  Type: {instance['InstanceType']}")
                if 'PublicIpAddress' in instance:
                    print(f"  Public IP: {instance['PublicIpAddress']}")
                print("  ---")
        
        # Test Bedrock access with batch inference
        print("\nTesting Bedrock batch inference...")
        bedrock_runtime = boto3.client('bedrock-runtime', **aws_config)
        
        # Batch of prompts
        prompts = [
            "Hello, this is test prompt 1.",
            "Hello, this is test prompt 2.",
            "Hello, this is test prompt 3."
        ]
        
        # Prepare batch request
        batch_request = {
            "prompts": prompts,
            "max_gen_len": 512,
            "temperature": 0.5,
            "top_p": 0.9
        }
        
        # Make batch request
        response = bedrock_runtime.invoke_model(
            modelId="meta.llama3-1-8b-instruct-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(batch_request)
        )
        
        print("\nBatch inference successful!")
        print("Response:", json.loads(response['body'].read()))
        
        # Test cross-region inference
        print("\nTesting cross-region inference...")
        # Initialize client for a different region
        bedrock_runtime_eu = boto3.client(
            'bedrock-runtime',
            region_name='eu-west-1',  # European region
            aws_access_key_id=aws_config['aws_access_key_id'],
            aws_secret_access_key=aws_config['aws_secret_access_key']
        )
        
        # Make request to European region
        response = bedrock_runtime_eu.invoke_model(
            modelId="meta.llama3-1-8b-instruct-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": "Hello from Europe!",
                "max_gen_len": 512,
                "temperature": 0.5,
                "top_p": 0.9
            })
        )
        
        print("\nCross-region inference successful!")
        print("Response:", json.loads(response['body'].read()))
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify the AWS credentials are correct")
        print("2. Verify the AWS regions are correct")
        print("3. Ensure your AWS account has access to Bedrock and EC2")
        print("4. Check if the model is available in your regions")
        print("5. Verify batch inference is supported for your model")
        print("6. Check if cross-region access is enabled")

if __name__ == "__main__":
    test_bedrock_access() 