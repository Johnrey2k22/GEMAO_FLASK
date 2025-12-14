# GEMAO Flask Application - Quick Start Guide

## Prerequisites
- Python 3.8 or higher
- MySQL Server (via XAMPP or standalone)
- pip (Python package manager)

## Installation Steps

### 1. Database Setup
Before running the application, ensure MySQL is running:
- Start MySQL server (via XAMPP Control Panel or standalone)
- Default credentials: `host=localhost, user=gemao_user, password=password`
- If different credentials, update MyFlaskapp/db.py

### 2. Virtual Environment Setup
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env with your settings (optional for development)
```

### 5. Run the Application
```bash
# Set Flask app (Windows PowerShell)
$env:FLASK_APP = "app"
$env:FLASK_ENV = "development"

# Set Flask app (Windows CMD)
set FLASK_APP=app
set FLASK_ENV=development

# Run the app
python app.py
# OR
flask run
```

The application will be available at: http://localhost:5000

## Default Login Credentials
- **Admin User**: 
  - Username: `admin`
  - Password: `admin_password`
  
- ** User**:
  - Username: ``
  - Password: `_password`
  
- **Regular User**:
  - Username: `user`
  - Password: `user_password`

## Project Structure
```
GEMAO-FLASK/
├── app.py                    # Entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── MyFlaskapp/               # Main application package
│   ├── __init__.py           # Flask app factory
│   ├── db.py                 # Database functions
│   ├── utils.py              # Utility functions
│   ├── auth/                 # Authentication blueprint
│   ├── user/                 # User dashboard blueprint
│   ├── admin/                # Admin panel blueprint
│   ├── /              #  panel blueprint
│   ├── games/                # Games blueprint
│   ├── leaderboard/          # Leaderboard blueprint
│   ├── tournaments/          # Tournament blueprint
│   ├── templates/            # HTML templates
│   └── static/               # CSS, JS, images
└── tests/                    # Test files
```

## Features Overview

### Authentication
- User registration with email OTP verification
- Login with role-based access control
- Session management with auto-timeout

### User Dashboard
- View available games
- See personal and game-specific leaderboards
- Edit user profile

### Games
10 Naruto-themed mini-games:
1. Naruto Run
2. Chakra Collector
3. Jutsu Battle
4. Ramen Eater
5. Ninja Maze
6. Sharingan Puzzle
7. Sage Mode Training
8. Akatsuki Hunt
9. Village Defense
10. Bijuu Capture

### Admin Features
- Add/manage users
- Add new games
- View system statistics

### Leaderboards
- Global leaderboard
- Game-specific leaderboards
- Top scores tracking

## Troubleshooting

### Database Connection Issues
- Ensure MySQL is running
- Verify credentials in MyFlaskapp/db.py
- Check that gemao_db database can be created

### Port Already in Use
```bash
# Use a different port
flask run --port 5001
```

### Missing Dependencies
```bash
# Reinstall all requirements
pip install --upgrade -r requirements.txt
```

## Development
- Enable debug mode: Set `FLASK_ENV=development` environment variable
- Check session data at: http://localhost:5000/debug/session
- Review logs in console for errors

## Production Deployment
1. Set `FLASK_ENV=production`
2. Use a production WSGI server (Gunicorn, Waitress)
3. Set secure `SECRET_KEY`
4. Enable `SESSION_COOKIE_SECURE=True` for HTTPS
5. Configure proper database credentials
6. Set up email service for OTP

## Support
For issues or questions, refer to the README.md file or the copilot-instructions.md file.
