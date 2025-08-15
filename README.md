# 🚀 Kelly's User Management System - Serverless Architecture

A **modern serverless web application** built with Flask + React, deployed on AWS Lambda with DynamoDB.

## ⚡ **Why Serverless?**

- 💰 **Pay only for what you use** - No servers running 24/7
- 🚀 **Infinite auto-scaling** - From 0 to thousands of requests
- 🛡️ **Zero server management** - AWS handles everything
- ⚡ **Global edge distribution** - Lightning-fast response times
- 🔒 **Built-in security** - AWS IAM and VPC protection

---

## 🏗️ **System Architecture**

### **Tech Stack:**
- **Frontend**: React 19.1.1 + Modern CSS (hosted on S3 + CloudFront)
- **Backend**: Flask 3.1.1 + Python 3.9 (AWS Lambda)
- **Database**: DynamoDB (NoSQL, serverless)
- **API**: AWS API Gateway (REST)
- **Deployment**: Serverless Framework
- **CI/CD**: GitHub Actions

### **AWS Services:**
- **AWS Lambda** - Serverless compute
- **DynamoDB** - NoSQL database
- **API Gateway** - HTTP routing
- **S3 + CloudFront** - Frontend hosting + CDN
- **IAM** - Security and permissions

---

## 🖥️ **Development Environment**

### **Prerequisites:**
- Python 3.9+
- Node.js 18+
- npm
- AWS CLI configured
- Serverless Framework

### **Setup & Installation:**

1. **Backend Setup:**
   ```bash
   cd python-app
   python3 -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   ```

3. **Install Serverless Framework:**
   ```bash
   npm install -g serverless
   npm install
   ```

---

## 🚀 **Quick Start**

### **Local Development:**

1. **Start DynamoDB Local (optional):**
   ```bash
   docker-compose -f docker-compose-serverless.yml up -d
   # Or use DynamoDB Local directly
   ```

2. **Start Backend API:**
   ```bash
   # Activate virtual environment
   source .venv/bin/activate
   
   # Run Flask app locally
   python3 web_app.py
   ```
   API runs at: `http://localhost:8080/api`

3. **Start Frontend:**
   ```bash
   cd frontend
   npm start
   ```
   Frontend runs at: `http://localhost:3000`

### **Test the Application:**
- Open: `http://localhost:3000`
- API Health: `http://localhost:8080/api/health`

---

## ☁️ **Serverless Deployment**

### **Deploy to AWS:**

1. **Configure AWS credentials:**
   ```bash
   aws configure
   ```

2. **Deploy with Serverless Framework:**
   ```bash
   # Production deployment
   ./deploy-serverless.sh production
   
   # Or manually:
   serverless deploy --stage production
   ```

3. **Deploy Frontend:**
   ```bash
   cd frontend
   npm run build
   # Deploy build/ to S3 bucket
   ```

### **GitHub Actions Deployment:**
Push to `main` branch for automatic deployment using `.github/workflows/deploy-serverless.yml`

**Required Repository Secrets:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

---

## 📊 **Project Structure**

```
python-app/
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── App.js              # Main React component
│   │   ├── App.css             # Kelly's custom styling
│   │   └── index.js
│   ├── public/
│   └── package.json
├── src/                        # Python backend
│   ├── models/
│   │   ├── dynamodb_user.py    # DynamoDB user model
│   │   └── __init__.py
│   ├── services/               # Business logic
│   ├── tests/                  # Test files
│   └── utils/                  # Helper functions
├── lambda_handler.py           # Lambda entry point
├── web_app.py                  # Flask application
├── serverless.yml              # Serverless configuration
├── requirements.txt            # Python dependencies
├── deploy-serverless.sh        # Deployment script
├── docker-compose-serverless.yml # Local DynamoDB
└── scripts/
    └── setup-dynamodb-local.sh
```

---

## 🔌 **API Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/users` | Get all users |
| `POST` | `/api/users` | Create new user |
| `GET` | `/api/users/{id}` | Get user by ID |
| `PUT` | `/api/users/{id}` | Update user |
| `DELETE` | `/api/users/{id}` | Delete user |

### **Example API Usage:**

```bash
# Health check
curl https://your-api.amazonaws.com/api/health

# Create user
curl -X POST https://your-api.amazonaws.com/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

---

## 🗄️ **Database Schema (DynamoDB)**

**Table**: `users`
- **Partition Key**: `user_id` (String)
- **Attributes**:
  - `username` (String)
  - `email` (String)
  - `first_name` (String)
  - `last_name` (String)
  - `created_at` (String, ISO 8601)
  - `updated_at` (String, ISO 8601)
  - `is_active` (Boolean)

---

## 🧪 **Testing**

```bash
# Run backend tests
source .venv/bin/activate
pytest

# Run with coverage
pytest --cov=src

# Frontend tests
cd frontend
npm test
```

---

## ⚙️ **Environment Variables**

### **Local Development:**
```bash
export FLASK_ENV=development
export SECRET_KEY=your-secret-key
export CORS_ORIGINS=http://localhost:3000
```

### **Production (Lambda):**
Set in `serverless.yml` or AWS Console:
- `SECRET_KEY`
- `CORS_ORIGINS`

---

## 🚀 **Available Commands**

```bash
# Backend
make install          # Install Python dependencies
make run              # Start Flask app
make test             # Run tests
make lint             # Code linting
make format           # Format code

# Frontend
cd frontend
npm start             # Development server
npm run build         # Production build
npm test              # Run tests

# Serverless
serverless deploy     # Deploy to AWS
serverless remove     # Remove from AWS
serverless logs -f app # View Lambda logs
```

---

## 🔒 **Security Features**

- ✅ **CORS protection** configured
- ✅ **Input validation** on all endpoints
- ✅ **AWS IAM permissions** for DynamoDB
- ✅ **HTTPS only** in production (API Gateway)
- ✅ **Environment variable** configuration
- ✅ **No hardcoded secrets**

---

## 💰 **Cost Estimation**

**Monthly AWS costs for typical usage:**

- **Lambda**: ~$0.20 per 1M requests
- **DynamoDB**: ~$1.25 per GB stored + read/write units
- **API Gateway**: ~$3.50 per 1M requests
- **S3 + CloudFront**: ~$0.50 for frontend hosting

**Total**: Approximately **$5-15/month** for small to medium applications

---

## 📈 **Benefits Over Traditional Hosting**

| **Serverless** | **Traditional Servers** |
|----------------|-------------------------|
| Pay-per-use | Fixed monthly costs |
| Auto-scaling | Manual scaling |
| Zero maintenance | Server management |
| Global edge | Single region |
| 99.99% uptime | Variable uptime |

---

## 🛠️ **Local Development with DynamoDB**

For local testing with DynamoDB Local:

```bash
# Start DynamoDB Local
docker-compose -f docker-compose-serverless.yml up -d

# Create tables
./scripts/setup-dynamodb-local.sh

# Access DynamoDB Admin UI
open http://localhost:8001
```

---

## 📚 **Useful Resources**

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [Serverless Framework Guide](https://www.serverless.com/framework/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/docs/)

---

## 🎯 **What's Next?**

- [ ] Add user authentication (AWS Cognito)
- [ ] Implement API rate limiting
- [ ] Add monitoring with CloudWatch
- [ ] Set up automated backups
- [ ] Add email notifications (SES)
- [ ] Implement caching (ElastiCache)

---

**Built with ❤️ using Flask, React, and AWS Serverless** 🚀

## 📞 **Support**

For questions or issues, please open an issue in the repository.

---

*Last updated: August 2025 - Serverless-Only Architecture*