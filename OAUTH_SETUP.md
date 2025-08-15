# 🔐 **OAuth Integration Setup Guide**

This guide will help you set up Google OAuth authentication for your KellyCo User Management System.

---

## 🎯 **Step 1: Create Google Cloud Project**

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a new project** or select existing one
3. **Enable the Google+ API** or **Google Identity Services**

---

## 🔧 **Step 2: Create OAuth 2.0 Credentials**

1. **Navigate to APIs & Services > Credentials**
2. **Click "Create Credentials" > "OAuth 2.0 Client ID"**
3. **Configure the consent screen** (if prompted):
   - Application name: `KellyCo User Management`
   - User support email: Your email
   - Developer contact: Your email
4. **Application type**: `Web application`
5. **Name**: `KellyCo Web App`
6. **Authorized origins**:
   ```
   http://localhost:3000
   http://localhost:8080
   https://yourdomain.com (for production)
   ```
7. **Authorized redirect URIs**:
   ```
   http://localhost:3000/login
   https://yourdomain.com/login (for production)
   ```

---

## 🔑 **Step 3: Get Your Credentials**

After creating the OAuth client, you'll get:
- **Client ID**: `your_actual_client_id.apps.googleusercontent.com`
- **Client Secret**: `your_actual_client_secret`

---

## ⚙️ **Step 4: Configure Environment Variables**

### **Backend (.env file in project root):**
```bash
# OAuth Configuration
GOOGLE_CLIENT_ID=your_actual_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_actual_client_secret

# Other existing variables...
AWS_REGION=us-east-1
DYNAMODB_TABLE=kelly-user-management-dev-users
DYNAMODB_LOCAL=true
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
CORS_ORIGINS=http://localhost:3000
```

### **Frontend (.env file in frontend/ directory):**
```bash
REACT_APP_API_URL=http://localhost:8080/api
REACT_APP_GOOGLE_CLIENT_ID=your_actual_client_id.apps.googleusercontent.com
```

---

## 🚀 **Step 5: Test the Setup**

1. **Start the backend**:
   ```bash
   source .venv/bin/activate
   export AWS_REGION=us-east-1
   python3 web_app.py
   ```

2. **Start the frontend** (in another terminal):
   ```bash
   cd frontend
   npm start
   ```

3. **Open browser**: http://localhost:3000
4. **Click "Sign in with Google"**
5. **Complete OAuth flow**

---

## 🔍 **How It Works**

### **OAuth Flow:**
1. **User clicks "Sign in with Google"**
2. **Google popup opens** for authentication
3. **User authenticates** with Google
4. **Google returns ID token** to frontend
5. **Frontend sends token** to backend `/api/auth/google`
6. **Backend verifies token** with Google
7. **Backend creates/finds user** in DynamoDB
8. **Backend returns user data** and JWT token
9. **Frontend stores user** and redirects to dashboard

### **User Data Stored:**
- Google ID (for future logins)
- Email address
- First name & Last name
- Profile picture URL
- Username (generated from email)
- OAuth provider ("google")

---

## 🛡️ **Security Features**

✅ **Token Verification**: Backend verifies Google tokens with Google servers  
✅ **JWT Session Management**: Secure session tokens for API access  
✅ **Automatic User Creation**: New users are automatically registered  
✅ **Account Linking**: Existing users can link Google accounts  
✅ **Secure Storage**: OAuth IDs stored securely in DynamoDB  

---

## 🎨 **User Experience**

### **Login Page Features:**
- **Primary**: Google OAuth login (prominent)
- **Secondary**: Legacy username/password (collapsible)
- **Loading states**: Visual feedback during authentication
- **Error handling**: Clear error messages for failures

### **Dashboard Enhancements:**
- **Profile pictures**: Show Google profile images
- **OAuth indicators**: Display "Signed in with Google"
- **Enhanced user cards**: Show OAuth login method

---

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **"OAuth not configured" error**:
   - Check that `GOOGLE_CLIENT_ID` is set in `.env`
   - Restart the Flask server after setting environment variables

2. **"Invalid Google token" error**:
   - Verify the Client ID matches between frontend and backend
   - Check that the domain is authorized in Google Cloud Console

3. **CORS errors**:
   - Ensure `CORS_ORIGINS` includes your frontend URL
   - Check that the frontend URL is authorized in Google Cloud Console

4. **DynamoDB errors**:
   - Make sure DynamoDB Local is running (if using local development)
   - Check AWS credentials (if using production DynamoDB)

---

## 🎯 **Production Deployment**

### **Update OAuth Origins:**
1. Add your production domain to Google Cloud Console
2. Update environment variables with production values
3. Use HTTPS for all OAuth redirects
4. Set secure `SECRET_KEY` for JWT signing

### **Environment Variables for Production:**
```bash
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
AWS_REGION=us-east-1
DYNAMODB_TABLE=kelly-user-management-prod-users
SECRET_KEY=your-very-secure-production-key
CORS_ORIGINS=https://yourdomain.com
```

---

## 🎉 **Benefits of OAuth Integration**

✅ **Enhanced Security**: No password storage required  
✅ **Better UX**: One-click login with existing Google accounts  
✅ **Automatic User Management**: Users are created automatically  
✅ **Profile Integration**: Automatic name and photo population  
✅ **Account Recovery**: Users can't lose access to their accounts  
✅ **Scalability**: Ready for multi-provider OAuth (GitHub, Microsoft, etc.)  

---

**Your KellyCo User Management System now supports modern OAuth authentication! 🚀**
