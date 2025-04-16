import boto3
import json
import time

def create_inference_profile():
    try:
        # Initialize Bedrock client
        bedrock = boto3.client(
            service_name='bedrock',
            region_name='us-east-1',
            aws_access_key_id='',  # Your access key
            aws_secret_access_key=''  # Your secret key
        )

        # First, request model access if not already granted
        print("Requesting model access...")
        try:
            bedrock.request_model_access(
                modelId='meta.llama3-1-8b-instruct-v1:0'
            )
            print("Model access requested successfully!")
        except Exception as e:
            print(f"Note: {str(e)}")
            print("This might mean you already have access to the model.")

        # Create a model customization job
        print("\nCreating model customization job...")
        job_name = f"llama3-customization-{int(time.time())}"
        
        response = bedrock.create_model_customization_job(
            jobName=job_name,
            customModelName='llama3-custom-model',
            roleArn='arn:aws:iam::YOUR_ACCOUNT_ID:role/service-role/AmazonBedrockCustomModelRole',
            baseModelIdentifier='meta.llama3-1-8b-instruct-v1:0',
            trainingDataConfig={
                's3Uri': 's3://YOUR_BUCKET/training-data.jsonl'
            },
            outputDataConfig={
                's3Uri': 's3://YOUR_BUCKET/output/'
            },
            hyperParameters={
                'epochCount': '1',
                'batchSize': '1',
                'learningRate': '0.00001'
            }
        )

        job_id = response['jobId']
        print(f"\nModel customization job created successfully!")
        print(f"Job ID: {job_id}")
        print("\nWaiting for job to complete...")

        # Wait for job to complete
        while True:
            status = bedrock.get_model_customization_job(jobId=job_id)['status']
            print(f"Current status: {status}")
            if status == 'COMPLETED':
                print("\nJob completed successfully!")
                break
            elif status == 'FAILED':
                print("\nJob failed!")
                break
            time.sleep(30)  # Check every 30 seconds

        # Get the model ARN
        model_arn = bedrock.get_model_customization_job(jobId=job_id)['outputModelArn']
        print(f"\nModel ARN: {model_arn}")

        # Print usage instructions
        print("\nTo use this model in your code:")
        print(f"modelId = '{model_arn}'")
        print("""
# Example usage:
response = bedrock_runtime.invoke_model(
    modelId=model_arn,
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
        "prompt": "Your prompt here",
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    })
)
""")

    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify your AWS credentials")
        print("2. Check if you have permissions to create model customization jobs")
        print("3. Ensure the model is available in your region")
        print("4. Verify your S3 bucket exists and is accessible")
        print("5. Make sure you have the correct IAM role")

if __name__ == "__main__":
    create_inference_profile() 