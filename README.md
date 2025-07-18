# Backend Deployment Guide

This guide explains how to deploy the Flask backend on various hosting platforms.

## Files Structure

```
backend/
├── app.py                 # Flask application setup
├── main.py               # Application entry point
├── models.py             # Database models
├── routes.py             # API endpoints
├── telegram_service.py   # Telegram integration
├── Procfile              # Heroku deployment config
├── runtime.txt           # Python version specification
└── requirements.txt      # Python dependencies (auto-generated)
```

## Platform-Specific Deployment

### Heroku Deployment

1. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=your_bot_token
   heroku config:set TELEGRAM_USER_ID=your_user_id
   heroku config:set SESSION_SECRET=your_secret_key
   ```

3. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### PythonAnywhere Deployment

1. **Upload Files**
   - Upload all Python files to your PythonAnywhere account
   - Place files in `/home/yourusername/mysite/`

2. **Create Virtual Environment**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.11 mysite
   pip install flask flask-cors flask-sqlalchemy requests gunicorn psycopg2-binary
   ```

3. **Configure Web App**
   - In PythonAnywhere dashboard, create a new web app
   - Set source code path to `/home/yourusername/mysite/`
   - Set WSGI configuration file to point to `main.py`

4. **Set Environment Variables**
   - Add environment variables in the "Environment Variables" section
   - Set `TELEGRAM_BOT_TOKEN`, `TELEGRAM_USER_ID`, `SESSION_SECRET`

### Railway Deployment

1. **Connect Repository**
   - Link your GitHub repository to Railway
   - Railway will auto-detect Python and use the Procfile

2. **Set Environment Variables**
   - In Railway dashboard, add environment variables:
     - `TELEGRAM_BOT_TOKEN`
     - `TELEGRAM_USER_ID`
     - `SESSION_SECRET`

3. **Deploy**
   - Railway will automatically deploy on git push

### Render Deployment

1. **Create Web Service**
   - Connect your GitHub repository
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn --bind 0.0.0.0:$PORT main:app`

2. **Environment Variables**
   - Add environment variables in Render dashboard
   - Set `TELEGRAM_BOT_TOKEN`, `TELEGRAM_USER_ID`, `SESSION_SECRET`

## Required Environment Variables

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_USER_ID=your_user_id_here

# Flask Configuration
SESSION_SECRET=your_secret_key_here

# Database Configuration (optional - defaults to SQLite)
DATABASE_URL=postgresql://user:password@host:port/database
```

## Getting Telegram Credentials

### 1. Create Telegram Bot

1. Open Telegram and search for "@BotFather"
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token (e.g., `1234567890:ABCdefGHIjklMNOpqrSTUvwxyz`)

### 2. Get Your User ID

1. Search for "@userinfobot" in Telegram
2. Send `/start` command
3. The bot will reply with your User ID
4. Copy the numeric ID (e.g., `123456789`)

## Database Configuration

### SQLite (Default)
- No configuration needed
- Database file created automatically
- Suitable for development and small deployments

### PostgreSQL (Recommended for Production)
- Set `DATABASE_URL` environment variable
- Format: `postgresql://user:password@host:port/database`
- Most hosting platforms provide PostgreSQL add-ons

## API Endpoints

### Health Check
```
GET /api/health
```

### Submit Tracking Data
```
POST /api/submit-data
Content-Type: application/json

{
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "accuracy": 10
  },
  "deviceInfo": {
    "platform": "MacIntel",
    "userAgent": "Mozilla/5.0...",
    "screen": {
      "width": 1920,
      "height": 1080
    }
  },
  "videoData": "data:video/webm;base64,..."
}
```

## CORS Configuration

The backend is configured to accept requests from any origin:

```python
CORS(app, origins=["*"], methods=["GET", "POST", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization", "Accept"])
```

For production, consider restricting origins to your frontend domain:

```python
CORS(app, origins=["https://your-frontend-domain.com"])
```

## Logging

The application uses Python's logging module with DEBUG level enabled.
Check your hosting platform's logs for debugging information.

## Testing

Test the deployment:

1. **Health Check**
   ```bash
   curl https://your-backend-domain.com/api/health
   ```

2. **Expected Response**
   ```json
   {
     "status": "healthy",
     "timestamp": "2024-01-01T00:00:00.000000",
     "version": "2.0.0"
   }
   ```

## Security Considerations

- Keep your Telegram bot token secure
- Use environment variables for sensitive data
- Consider rate limiting in production
- Use HTTPS for all communication
- Validate all input data
- Consider implementing authentication if needed

## Troubleshooting

### Common Issues:

1. **Module Not Found**: Ensure all dependencies are installed
2. **Database Connection**: Check DATABASE_URL format
3. **CORS Errors**: Verify CORS configuration
4. **Telegram Errors**: Check bot token and user ID
5. **Port Issues**: Ensure app binds to correct port

### Debug Commands:

```bash
# Check environment variables
echo $TELEGRAM_BOT_TOKEN

# Test database connection
python -c "from app import db; print(db.engine.url)"

# Check installed packages
pip list
```
