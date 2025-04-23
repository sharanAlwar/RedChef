# helm-redchef

A Helm chart to deploy RedChef — an application that connects to Amazon Bedrock using Meta’s LLaMA 3 70B model. This chart sets up both frontend and backend components, with Redis and AWS integration. Everything is deployed into a dedicated Kubernetes namespace: `redchef`.

---

## 🚀 Quick Start

### 1. Download the Default `values.yaml`

Start by downloading the default values file:

helm show values redchef/helm-redchef > custom-values.yaml

### 2. Configure AWS and Redis Credentials

Open the custom-values.yaml file and update the following:

namespace: redchef

frontendConfig:  
 VITE_BACKEND_URL: "http://backend.redchef.svc.cluster.local:8000"

backendConfig:  
 AWS_ACCESS_KEY_ID: "<your-access-key-id>"  
 AWS_SECRET_ACCESS_KEY: "<your-secret-access-key>"  
 AWS_REGION: "us-east-1"  # Or your target AWS region  
 REDIS_HOST: "redis-service.redchef.svc.cluster.local"

⚠️ The AWS credentials must have permissions to access Amazon Bedrock, specifically the Meta LLaMA 3 70B model:

- bedrock:InvokeModel  
- bedrock:InvokeModelWithResponseStream

### 3. Install the Chart

Once your custom-values.yaml is ready, deploy RedChef:

helm install redchef redchef/helm-redchef -f custom-values.yaml --create-namespace --namespace redchef

To upgrade an existing deployment:

helm upgrade redchef redchef/helm-redchef -f custom-values.yaml --namespace redchef

### 4. Verify the Deployment

After installation, verify:

- The backend pod connects successfully to Amazon Bedrock and Redis  
- The frontend app communicates with the backend via the configured URL  
- All components are running in the redchef namespace:

kubectl get all -n redchef

---

## 📦 Chart Details

- **Chart Name:** helm-redchef  
- **Version:** 0.1.0  
- **App Version:** 1.0.0  
- **Namespace:** redchef  
- **Maintainers:** https://github.com/sharanAlwar  
- **Source:** https://github.com/sharanAlwar/RedChef.git
