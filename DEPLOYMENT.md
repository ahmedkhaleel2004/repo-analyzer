# Deployment Guide

## Understanding FastAPI

FastAPI is a modern Python web framework that automatically creates REST APIs with:

- Automatic API documentation (Swagger UI at `/docs`)
- Type validation using Python type hints
- Async support for better performance
- Built-in JSON serialization/deserialization

In our app:

- `@app.get("/")` creates a GET endpoint at the root URL
- `@app.get("/analyze/{org}")` creates a dynamic route where `{org}` is a parameter
- FastAPI automatically generates OpenAPI/Swagger documentation

## Deploying to Railway

Railway is a modern cloud platform that makes deploying apps simple. Here's how to deploy this repo analyzer:

### Prerequisites

1. Create a Railway account at [railway.app](https://railway.app)
2. Install Railway CLI: `brew install railway` (macOS) or see [docs](https://docs.railway.app/develop/cli)
3. Make sure you have your GitHub PAT token ready

### Method 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub**

   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push
   ```

2. **Connect to Railway**

   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your `repo-analyzer` repository
   - Railway will auto-detect the Dockerfile

3. **Set Environment Variables**

   - In Railway dashboard, go to your project
   - Click on the service
   - Go to "Variables" tab
   - Add: `GITHUB_TOKEN` or `GITHUB_PAT` with your token value
   - Railway will redeploy automatically

4. **Access Your App**
   - Railway provides a public URL like `https://repo-analyzer-production.up.railway.app`
   - Visit `/docs` for API documentation
   - Use `/analyze/SocketDev` to analyze an organization

### Method 2: Deploy via CLI

1. **Login to Railway**

   ```bash
   railway login
   ```

2. **Initialize Project**

   ```bash
   # In your repo-analyzer directory
   railway init
   # Choose "Empty Project" and give it a name
   ```

3. **Set Environment Variables**

   ```bash
   railway variables set GITHUB_TOKEN=your_token_here
   ```

4. **Deploy**

   ```bash
   railway up
   ```

5. **Generate Domain**
   ```bash
   railway domain
   ```

### Using the Deployed API

Once deployed, you can:

1. **Check Health**

   ```bash
   curl https://your-app.railway.app/
   ```

2. **Analyze an Organization**

   ```bash
   curl https://your-app.railway.app/analyze/microsoft
   ```

3. **Get Previous Results**

   ```bash
   curl https://your-app.railway.app/results/microsoft
   ```

4. **View API Docs**
   - Visit `https://your-app.railway.app/docs` in your browser

### Monitoring & Logs

- In Railway dashboard, click on your deployment
- View real-time logs in the "Logs" tab
- Monitor resource usage in "Metrics" tab
- Set up alerts for errors or high usage

### Updating Your App

When you make changes:

1. **Via GitHub (if connected)**

   ```bash
   git add .
   git commit -m "Update feature X"
   git push
   ```

   Railway auto-deploys on push to main branch

2. **Via CLI**
   ```bash
   railway up
   ```

### Troubleshooting

1. **401 Unauthorized Error**

   - Check if `GITHUB_TOKEN` or `GITHUB_PAT` is set in Railway variables
   - Verify token has correct permissions (public_repo scope)

2. **Timeout Errors**

   - Large organizations may take time to analyze
   - Consider implementing caching (SQLite) for production

3. **Rate Limit Issues**
   - GitHub allows 5000 requests/hour with token
   - Our GraphQL queries are efficient but monitor usage

### Production Considerations

1. **Add Caching**

   - Implement SQLite caching in `fetcher.py`
   - Cache results for 1 hour to reduce API calls

2. **Add Authentication**

   - Protect your API with API keys
   - Use FastAPI's security features

3. **Set Resource Limits**

   - Configure memory/CPU limits in Railway
   - Add request timeouts

4. **Enable CORS** (if building a frontend)

   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### Example API Usage

```python
import requests

# Analyze an organization
response = requests.get("https://your-app.railway.app/analyze/vercel")
data = response.json()

print(f"Average score: {data['average_score']}")
for repo, score in data['repository_scores'].items():
    print(f"{repo}: {score}/100")
```

## Alternative Deployment Options

### Docker (Local/VPS)

```bash
docker build -t repo-analyzer .
docker run -d \
  -e GITHUB_TOKEN=your_token \
  -p 8000:8000 \
  --name repo-analyzer \
  repo-analyzer
```

### Fly.io

```bash
fly launch
fly secrets set GITHUB_TOKEN=your_token
fly deploy
```

### Google Cloud Run

```bash
gcloud run deploy repo-analyzer \
  --source . \
  --set-env-vars GITHUB_TOKEN=your_token \
  --region us-central1
```

## Cost Considerations

- Railway's free tier includes 500 hours/month
- This app uses minimal resources (~256MB RAM)
- Costs: ~$5-10/month for 24/7 operation
- Consider scheduled scaling for cost optimization
