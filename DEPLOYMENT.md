# Deployment Guide - PrediX Markets

This guide will help you deploy your prediction marketplace to Vercel and set up the backend API.

## 🚀 Vercel Frontend Deployment

### Step 1: Connect to Vercel
1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "New Project"
3. Import your repository: `bobanuu/prediction_market`
4. Set the **Root Directory** to `frontend`
5. Vercel will auto-detect it's a React app

### Step 2: Environment Variables
In Vercel dashboard, add these environment variables:
```bash
REACT_APP_API_URL=https://your-backend-url.herokuapp.com
```

### Step 3: Deploy
Click "Deploy" - Vercel will build and deploy your React app automatically!

## 🔧 Backend API Deployment Options

### Option 1: Heroku (Recommended)
```bash
# Install Heroku CLI
npm install -g heroku

# Login to Heroku
heroku login

# Create Heroku app
heroku create your-prediction-market-api

# Add PostgreSQL database
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com

# Deploy
git subtree push --prefix=. heroku main
```

### Option 2: Railway
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Select the root directory (not frontend)
4. Add environment variables in Railway dashboard
5. Deploy automatically

### Option 3: Render
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python manage.py runserver`
6. Add environment variables

## 🔗 Connecting Frontend to Backend

### Update Vercel Environment Variables
Once your backend is deployed, update the Vercel environment variable:
```bash
REACT_APP_API_URL=https://your-actual-backend-url.com
```

### CORS Configuration
Make sure your Django backend allows requests from your Vercel domain:
```python
# In settings.py
CORS_ALLOWED_ORIGINS = [
    "https://your-app.vercel.app",
    "http://localhost:3000",  # For development
]
```

## 📊 Database Setup

### For Production (PostgreSQL)
```python
# In settings.py - add to production settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
    }
}
```

### Run Migrations
```bash
# On your production server
python manage.py migrate
python manage.py shell -c "exec(open('create_sample_data.py').read())"
```

## 🎯 Final Steps

1. **Test the deployment**: Visit your Vercel URL
2. **Create admin user**: Use Django admin or shell
3. **Verify API connection**: Check browser network tab
4. **Test trading**: Place a test order

## 🔍 Troubleshooting

### Common Issues:
- **CORS errors**: Check CORS_ALLOWED_ORIGINS in Django settings
- **API not found**: Verify REACT_APP_API_URL in Vercel
- **Database errors**: Run migrations on production
- **Authentication issues**: Check session settings

### Debug Commands:
```bash
# Check Vercel logs
vercel logs

# Check Heroku logs
heroku logs --tail

# Test API locally
curl https://your-api-url.com/api/markets/
```

## 📱 Your Live URLs
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-api.herokuapp.com`
- **Admin**: `https://your-api.herokuapp.com/admin/`

Your prediction marketplace will be live and ready for trading! 🎉
