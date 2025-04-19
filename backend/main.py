from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
import json
import os
import logging
from dotenv import load_dotenv
import redis
import hashlib
import re
from typing import List, Dict, Optional
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis client
logger.info("Initializing Redis client...")
redis_host = os.getenv('REDIS_HOST', 'redis-service.default.svc.cluster.local','')  # Update this to your service name
redis_port = int(os.getenv('REDIS_PORT', 6379))
try:

    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=0,
        decode_responses=True
    )
    # Test the connection
    redis_client.ping()
    logger.info("Redis client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Redis client: {str(e)}")
    raise

# Initialize Bedrock client
logger.info("Initializing Bedrock client...")
try:
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    logger.info("Bedrock client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Bedrock client: {str(e)}")
    raise

class RecipeRequest(BaseModel):
    ingredients: List[str]
    cuisine_type: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None

class RecipeResponse(BaseModel):
    cuisine_name: str
    steps: List[str]
    suggested_ingredients: List[str]

def generate_recipe(ingredients: List[str], cuisine_type: Optional[str] = None) -> Dict:
    try:
        # Create the prompt with special tokens
        prompt = f"""<|begin_of_text|>
<|start_header_id|>system<|end_header_id|>
You are a trendy chef creating American-style fusion recipes for Indian users. Your task is to create a recipe using the given ingredients and format it as a JSON object. The cuisine name should be short, memorable, and appeal to Indian users who enjoy American food trends.

If any ingredients don't work well together or aren't needed for the dish, mention this in a separate suggestion. Focus on creating fusion dishes that blend American trends with familiar flavors.
<|eot_id|>

<|start_header_id|>user<|end_header_id|>
Create a recipe using these ingredients: {', '.join(ingredients)}.
The cuisine name should be:
1. Short and catchy (2-3 words max)
2. Use trendy American food terms (e.g. "Loaded", "Smashed", "Epic")
3. Sound delicious and modern

Examples of good names:
- "Epic Burger Bowl"
- "Loaded Potato Stack"
- "Smashed Sandwich Magic"
- "Crispy Ranch Bites"

Format the response as a JSON object with this structure:
{{
  "cuisine_name": "string",
  "steps": [
    "string",
    "string",
    "string"
  ],
  "suggested_ingredients": [
    "string",  // First suggestion - either an enhancement or note about incompatible ingredients
    "string"   // Second suggestion - either an enhancement or note about incompatible ingredients
  ]
}}

For the suggested_ingredients:
- If all ingredients work well together, suggest two ingredients that would enhance the dish
- If any ingredients don't fit well, use one suggestion to explain which ingredient(s) might not be needed and why
- Format enhancement suggestions like: "Crispy bacon bits - adds a savory American-style crunch"
- Format compatibility notes like: "Note: The [ingredient] isn't needed here - it doesn't fit with this style of dish"

Examples of good suggestions:
- "Ranch seasoning - adds that classic American flavor everyone loves"
- "Note: The cardamom isn't needed here - this dish works better with simple American spices"
- "Crispy onions - gives that trendy burger-joint crunch"
<|eot_id|>

<|start_header_id|>assistant<|end_header_id|>"""

        # Make the request to Bedrock
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
        
        # Parse the response
        response_body = json.loads(response['body'].read().decode('utf-8'))
        generation_text = response_body.get('generation', '')
        
        if not generation_text:
            raise HTTPException(status_code=500, detail="No response generated from the model")
        
        # Extract JSON from the response
        json_match = re.search(r'\{[\s\S]*\}', generation_text)
        if not json_match:
            raise HTTPException(status_code=500, detail="Could not parse recipe from model response")
        
        recipe_json = json_match.group(0)
        recipe = json.loads(recipe_json)
        
        return recipe
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Bedrock error: {error_code} - {error_message}")
        raise HTTPException(
            status_code=500,
            detail=f"AWS Bedrock error: {error_code} - {error_message}"
        )
    except Exception as e:
        logger.error(f"Error generating recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-recipe", response_model=RecipeResponse)
async def create_recipe(request: RecipeRequest):
    try:
        # Create cache key
        cache_key = f"recipe:{':'.join(sorted(request.ingredients))}:{request.cuisine_type or 'any'}"
        
        # Check cache
        cached_recipe = redis_client.get(cache_key)
        if cached_recipe:
            logger.info("Returning cached recipe")
            return json.loads(cached_recipe)
        
        # Generate new recipe
        recipe = generate_recipe(request.ingredients, request.cuisine_type)
        
        # Cache the result
        redis_client.setex(cache_key, 3600, json.dumps(recipe))  # Cache for 1 hour
        
        return recipe
        
    except Exception as e:
        logger.error(f"Error in create_recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 