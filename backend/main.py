from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
import json
import os
import logging
from dotenv import load_dotenv
import redis
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis client
logger.info("Initializing Redis client...")
redis_client = redis.Redis(
    host='redis',
    port=6379,
    db=0,
    decode_responses=True
)
logger.info("Redis client initialized successfully")

# Initialize Bedrock client
logger.info("Initializing Bedrock client...")
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
logger.info("Bedrock client initialized successfully")

class RecipeRequest(BaseModel):
    ingredients: list[str]

def create_prompt(ingredients: list[str]) -> str:
    return f"""Given the ingredients: {', '.join(ingredients)}

Generate:
1. A creative, attractive cuisine name that would excite a professional chef or foodie.
2. Detailed cooking instructions in Gordon Ramsay's tone—precise, high-energy, and professional.

Respond in JSON format:
{{
  "cuisine_name": "Your amazing dish name",
  "steps": [
    "Step 1...",
    "Step 2...",
    ...
  ]
}}"""

def generate_cache_key(ingredients: list[str]) -> str:
    """Generate a unique cache key for the ingredients list."""
    ingredients_str = ','.join(sorted(ingredients))
    temp = hashlib.md5(ingredients_str.encode()).hexdigest()
    print(temp)
    logger.error("Temp vallue"+temp)
    return temp

@app.post("/generate-recipe")
async def generate_recipe(request: RecipeRequest):
    try:
        logger.info(f"Received recipe request with ingredients: {request.ingredients}")
        
        # Generate cache key
        cache_key = generate_cache_key(request.ingredients)
        
        # Check Redis cache
        cached_recipe = redis_client.get(cache_key)
        if cached_recipe:
            logger.info("Recipe found in cache")
            return json.loads(cached_recipe)
        
        logger.info("Recipe not found in cache, generating new recipe")
        prompt = create_prompt(request.ingredients)
        logger.info("Created prompt successfully")
        
        # Prepare the request body
        body = {
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 1
        }
        logger.info(f"Prepared request body: {json.dumps(body, indent=2)}")
        
        # Make the request to Bedrock
        logger.info("Making request to Bedrock API...")
        logger.info(f"Using model ID: deepseek.r1-v1:0")
        
        response = bedrock.invoke_model(
            modelId='deepseek.r1-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps(body)
        )
        logger.info("Received response from Bedrock API")
        
        # Parse the response
        response_body = json.loads(response.get('body').read())
        logger.info(f"Parsed response body: {json.dumps(response_body, indent=2)}")
        
        # Extract the completion from the response
        completion = response_body.get('completion', '')
        try:
            # Try to parse the completion as JSON
            recipe_data = json.loads(completion)
            
            # Cache the recipe for 24 hours
            redis_client.setex(
                cache_key,
                86400,  # 24 hours in seconds
                json.dumps(recipe_data)
            )
            logger.info("Recipe cached successfully")
            
            return recipe_data
        except json.JSONDecodeError:
            # If parsing fails, return the raw completion
            return {"error": "Failed to parse response", "raw_response": completion}
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No additional details'}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 