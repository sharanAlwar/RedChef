import boto3
import json
import re

def test_llama3():
    try:
        # Initialize Bedrock client
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1',
            aws_access_key_id='',  # Your access key
            aws_secret_access_key=''  # Your secret key
        )

        # Test recipe generation prompt
        prompt = """<|begin_of_text|>
<|start_header_id|>system<|end_header_id|>
You are a professional chef creating a recipe. Your task is to create a recipe using the given ingredients and format it as a JSON object.
<|eot_id|>

<|start_header_id|>user<|end_header_id|>
Create a recipe using these ingredients: chicken, rice, vegetables.
Format the response as a JSON object with this structure:
{
  "cuisine_name": "string",
  "steps": [
    "string",
    "string",
    "string"
  ]
}
<|eot_id|>

<|start_header_id|>assistant<|end_header_id|>"""
        
        # Make the request
        print("Making request to Llama 3 70B...")
        response = bedrock_runtime.invoke_model(
            modelId="meta.llama3-70b-instruct-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": prompt,
                "max_gen_len": 1024,
                "temperature": 0.7,
                "top_p": 0.95
            })
        )
        
        # Parse and print the response
        response_body = json.loads(response['body'].read().decode('utf-8'))
        print("\nResponse:")
        print(json.dumps(response_body, indent=2))
        
        # Extract the generation text
        generation_text = response_body.get('generation', '')
        if not generation_text:
            print("\nNo response generated. Try adjusting the prompt or parameters.")
            return
            
        # Try to extract JSON from the response
        try:
            # Find JSON object in the response using regex
            json_match = re.search(r'\{[\s\S]*\}', generation_text)
            if json_match:
                recipe_json = json_match.group(0)
                recipe = json.loads(recipe_json)
                print("\nParsed Recipe:")
                print(f"Cuisine Name: {recipe['cuisine_name']}")
                print("\nSteps:")
                for i, step in enumerate(recipe['steps'], 1):
                    print(f"{i}. {step}")
            else:
                print("\nCould not find JSON object in response. Raw response:")
                print(generation_text)
        except json.JSONDecodeError:
            print("\nCould not parse the response as JSON. Raw response:")
            print(generation_text)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify your AWS credentials")
        print("2. Make sure you have requested access to the Llama 3 70B model")
        print("3. Check if the model is available in your region")

if __name__ == "__main__":
    test_llama3() 