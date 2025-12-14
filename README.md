# GEMAO Flask Naruto Game Platform

A production-ready Flask web application featuring Naruto-themed games, user authentication, and leaderboards.

## Features

- **Personal Website**: Home page with Naruto theme
- **Authentication System**: Login/logout with role-based access (user, , admin)
- **Game Platform**: 10 Naruto-themed mini-games built with Pygame
- **Leaderboards**: Score tracking and ranking system
- **Admin Panel**: Manage users and games

## Architecture

Flask factory pattern

Blueprint-based structure:

- auth
- admin
- user
- games
- leaderboard

## Tech Stack

- Flask
- Jinja2
- MySQL (XAMPP)
- SMTP
- PyMySQL / MySQL Connector
- HTML / CSS / JS

## Installation

### Prerequisites
- Python 3.8+
- MySQL (via XAMPP)
- Git

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd GEMAO-FLASK
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install flask mysql-connector-python pygame
   ```

4. **Setup MySQL Database**:
   - Start XAMPP and ensure MySQL is running
   - Open phpMyAdmin (http://localhost/phpmyadmin)
   - Create database `gemao_db`
   - Create user `gemao_user` with password `password` and grant all privileges on `gemao_db`
   - Or update credentials in `MyFlaskapp/db.py` to match your MySQL setup

5. **Run the application**:
   ```bash
   $env:FLASK_APP = "MyFlaskapp"
   flask run
   ```

## Database Schema

### Tables
- `user_tb`: User accounts with roles
- `games_tb`: Game metadata
- `scores_tb`: User scores and timestamps

### Default Users
- **Admin**: username=admin, password=admin_password
- ****: username=, password=_password
- **User**: username=user, password=user_password

## Games

All games are located in `MyFlaskapp/games/` and use Pygame with OOP principles:

1. **Chakra Typing Game**: Test your typing speed while collecting chakra
2. **Clash Game Enhanced**: Enhanced clash battle game with special moves
3. **Hand Sign Memory Game**: Memorize and repeat ninja hand signs
4. **Ninja Cat Game**: Guide the ninja cat through obstacles
5. **Ramen Shop Game**: Serve ramen to customers quickly
6. **Roof Run Game**: Run across rooftops avoiding obstacles
7. **Shadow Clone Whack-a-Mole**: Hit shadow clones as they appear
8. **Sharingan Difference Game**: Find differences using Sharingan eyes
9. **Shuriken Game**: Throw shurikens at targets
10. **Tree Climbing Game**: Climb trees using chakra control

## Deployment

### Local Development
- Run `flask run` with virtual environment activated
- Access at http://localhost:5000

### Production Deployment
1. Set environment variables:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secret-key
   ```

2. Use a WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 MyFlaskapp:create_app()
   ```

3. Configure reverse proxy (nginx/apache) for static files and SSL

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
```

## API Endpoints

- `GET /`: Home page
- `GET /login`: Login page
- `POST /login`: Authenticate user
- `GET /logout`: Logout
- `GET /games/`: List games
- `GET /games/play/<id>`: Play game page
- `POST /games/submit_score/<id>`: Submit score
- `GET /leaderboard/`: View leaderboard
- `GET /admin/dashboard`: Admin panel (admin only)

## Security Notes

- Passwords are stored in plain text (development only)
- Use hashed passwords in production
- Configure proper session settings
- Enable CSRF protection for forms

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## License

MIT License