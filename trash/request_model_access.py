import boto3
import json

def request_model_access():
    try:
        # Initialize Bedrock client
        bedrock = boto3.client(
            service_name='bedrock',
            region_name='us-east-1',
            aws_access_key_id='',  # Your access key
            aws_secret_access_key=''  # Your secret key
        )

        # List available foundation models
        print("Listing available foundation models...")
        response = bedrock.list_foundation_models()
        
        # Print available models
        print("\nAvailable models:")
        for model in response.get('modelSummaries', []):
            print(f"- {model['modelId']}")
            
        # Check if Llama 3 is available
        llama3_model = next((m for m in response.get('modelSummaries', []) 
                           if m['modelId'] == 'meta.llama3-1-8b-instruct-v1:0'), None)
        
        if llama3_model:
            print("\nLlama 3 model is available!")
            print("Model details:")
            print(f"Provider: {llama3_model['providerName']}")
            print(f"Status: {llama3_model.get('modelStatus', 'N/A')}")
            
            # Try to use the model
            print("\nTesting model access...")
            bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                region_name='us-east-1',
                aws_access_key_id='AKIAYPD2IC63YKGQSY6G',  # Your access key
                aws_secret_access_key='kfcp1tUqUDral0OOHv7r0V1Lj1Pil66yIUo0F/h5'  # Your secret key
            )
            
            try:
                response = bedrock_runtime.invoke_model(
                    modelId='meta.llama3-1-8b-instruct-v1:0',
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps({
                        "prompt": "Hello, this is a test.",
                        "max_gen_len": 512,
                        "temperature": 0.5,
                        "top_p": 0.9
                    })
                )
                print("\nModel access test successful!")
            except Exception as e:
                print(f"\nModel access test failed: {str(e)}")
                print("\nTo request access to this model:")
                print("1. Go to AWS Bedrock Console")
                print("2. Navigate to 'Model access'")
                print("3. Find 'Meta Llama 3 8B Instruct'")
                print("4. Click 'Request model access'")
        else:
            print("\nLlama 3 model is not available in your region.")
            print("Please check if it's available in other regions.")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify your AWS credentials")
        print("2. Check if you have permissions to access Bedrock")
        print("3. Ensure you're using the correct region")

if __name__ == "__main__":
    request_model_access() 