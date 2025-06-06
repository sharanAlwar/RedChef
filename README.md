# RedChef - AI-Powered Recipe Generator

RedChef is an innovative recipe generation application that uses AWS Bedrock's Llama 3 70B model to create unique, trendy recipes based on available ingredients. The application features a modern React frontend and a FastAPI backend, with Redis caching for improved performance.

## Features

- AI-powered recipe generation using AWS Bedrock's Llama 3 70B model
- Trendy and catchy recipe names
- Detailed cooking instructions in a professional chef's style
- Smart ingredient suggestions to enhance dishes
- Modern React frontend with responsive design
- FastAPI backend with Redis caching
- Real-time recipe generation
- CORS-enabled for secure frontend-backend communication

## Recipe Generation Features

1. **Trendy Recipe Names**
   - Short and catchy (2-3 words)
   - Uses modern food terminology
   - Appealing and memorable

2. **Detailed Cooking Steps**
   - Clear, step-by-step instructions
   - Professional chef's guidance
   - Easy to follow format

3. **Smart Ingredient Suggestions**
   - Two additional ingredients to enhance the dish
   - Explanations for why each ingredient works
   - Professional culinary insights

## Architecture

The application consists of three main components:

1. **Frontend (React)**
   - Built with Vite
   - Modern UI with dark theme
   - Interactive ingredient management
   - Real-time recipe display
   - Runs on port 5173

2. **Backend (FastAPI)**
   - Python-based API server
   - Integrates with AWS Bedrock's Llama 3 70B model
   - Implements Redis caching for recipe storage
   - Runs on port 8000

3. **Redis Cache**
   - In-memory data store
   - Caches generated recipes for 1 hour
   - Improves response times for frequently requested recipes
   - Runs on port 6379

## Redis Implementation

The application uses Redis for caching generated recipes to improve performance and reduce API calls to AWS Bedrock. Here's how it works:

1. When a recipe request is made, the system first checks Redis for a cached recipe
2. If found, the cached recipe is returned immediately
3. If not found, a new recipe is generated using AWS Bedrock
4. The new recipe is cached in Redis for 1 hour
5. Subsequent requests for the same ingredients will use the cached version

Benefits of Redis caching:
- Faster response times for repeated requests
- Reduced AWS Bedrock API usage
- Lower latency for users
- Cost optimization for API calls

## Prerequisites

- Docker and Docker Compose
- AWS account with Bedrock access
- AWS credentials (access key and secret key)
- Access to Llama 3 70B model in AWS Bedrock

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd RedChef
   ```

2. Set up environment variables as described above

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Redis: localhost:6379

## API Endpoints

- `POST /generate-recipe`
  - Request body:
    ```json
    {
      "ingredients": ["ingredient1", "ingredient2", ...],
      "cuisine_type": "optional_cuisine_type",
      "dietary_restrictions": ["optional_restriction1", ...]
    }
    ```
  - Returns:
    ```json
    {
      "cuisine_name": "Trendy Recipe Name",
      "steps": ["Step 1...", "Step 2...", ...],
      "suggested_ingredients": [
        "Ingredient 1 - reason for enhancement",
        "Ingredient 2 - reason for enhancement"
      ]
    }
    ```

- `GET /health`
  - Returns: Health check status of the API

## Development

- Frontend development server runs on port 5173
- Backend API runs on port 8000
- Redis runs on port 6379
- Hot-reloading enabled for both frontend and backend

## License

This project is licensed under the MIT License - see the LICENSE file for details.
