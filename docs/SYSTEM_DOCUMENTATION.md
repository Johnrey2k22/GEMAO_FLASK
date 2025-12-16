# GEMAO Flask Application - Complete System Documentation

## System Overview

GEMAO is a comprehensive Flask-based web application implementing a Naruto-themed gaming platform with user authentication, game management, leaderboards, and administrative features. The system follows professional software engineering practices including the Factory Pattern, Blueprints, MVC architecture, and Object-Oriented Programming principles.

## Project Structure

### Core Application Files
- **app.py** - Application entry point; creates Flask app using factory pattern
- **requirements.txt** - Python package dependencies
- **.env.example** - Environment variable template for configuration
- **config.py** - Configuration settings for different environments

### Application Package (MyFlaskapp/)
- **__init__.py** - Application factory function `create_app()`
- **db.py** - Database connection, table creation, and utility functions
- **utils.py** - Shared utilities (validation, email, OTP, alerts)
- **models.py** - Abstract base classes and data models
- **config.py** - Configuration classes for environment-based settings

### Blueprints (Modular Application Components)

#### Auth Blueprint (MyFlaskapp/auth/)
Handles user authentication and registration
- **Routes**:
  - `POST /auth/login` - User login
  - `GET /auth/logout` - User logout
  - `GET/POST /auth/register` - User registration
  - `GET/POST /auth/verify_otp` - OTP verification
  - `GET /auth/resend_otp` - Resend OTP
  - `GET/POST /auth/profile` - User profile management

#### User Blueprint (MyFlaskapp/user/)
User dashboard and profile management
- **Routes**:
  - `GET /user/dashboard` - User dashboard with games and leaderboards
  - `GET/POST /user/profile` - User profile view and edit

#### Admin Blueprint (MyFlaskapp/admin/)
Administrative panel for system management
- **Routes**:
  - `GET /admin/dashboard` - Admin dashboard with statistics
  - `GET/POST /admin/add_user` - Add new user
  - `GET/POST /admin/verify_add_user_otp` - Verify new user via OTP
  - `GET/POST /admin/add_game` - Add new game
  - `GET /admin/users` - List all users
  - `GET /admin/games` - List all games
  - `DELETE /admin/users/<id>` - Delete user
  - `DELETE /admin/games/<id>` - Delete game

#### Games Blueprint (MyFlaskapp/games/)
Game management and gameplay
- **Routes**:
  - `GET /games/` - List all games
  - `GET/POST /games/play/<game_id>` - Play game and submit score
  - `POST /games/submit_score/<game_id>` - Submit game score

#### Leaderboard Blueprint (MyFlaskapp/leaderboard/)
Score tracking and ranking
- **Routes**:
  - `GET /leaderboard/` - Global leaderboard
  - `GET /leaderboard/game/<game_id>` - Game-specific leaderboard

### Templates (MyFlaskapp/templates/)
Jinja2 HTML templates with Naruto theme:
- **base.html** - Base template with navbar, footer, styling
- **home.html** - Landing page
- **auth/** - Login, register, profile, OTP verification templates
- **user/** - User dashboard and profile templates
- **admin/** - Admin dashboard, user/game management templates
- **games/** - Games list and play templates
- **leaderboard/** - Leaderboard templates

### Static Files (MyFlaskapp/static/)
- **images/** - Naruto-themed images (background, characters, obstacles, power-ups)
- **sounds/** - Game audio files (background music, sound effects)
- **favicon.ico** - Browser tab icon
- **css/** - Stylesheets (if used)

### Games Module (MyFlaskapp/games/)
10 Naruto-themed mini-games built with Pygame:

1. **chakra_typing_game.py** - Chakra Typing Game
2. **clash_game_enhanced.py** - Clash Game Enhanced
3. **hand_sign_memory_game.py** - Hand Sign Memory Game
4. **ninja_cat_game.py** - Ninja Cat Game
5. **ramen_shop_game.py** - Ramen Shop Game
6. **roof_run_game.py** - Roof Run Game
7. **shadow_clone_whack_a_mole.py** - Shadow Clone Whack-a-Mole
8. **sharingan_difference_game.py** - Sharingan Difference Game
9. **shuriken_game.py** - Shuriken Game
10. **tree_climbing_game.py** - Tree Climbing Game

Each game inherits from `game_base.py` (abstract base class) demonstrating OOP principles.

## Database Architecture

### Tables
- **users** - User account information (id, user_id, username, password_hash, email, user_type, etc.)
- **user_profiles** - Extended user information (profile_image, personal_intro, dream_it_job)
- **games** - Game definitions (name, description, file_path, max_score)
- **game_access** - User-game access control
- **leaderboards** - Score records (game_id, user_id, score, created_at)
- **tournaments_tb** - Tournament definitions
- **tournament_participants_tb** - Tournament participants
- **matches_tb** - Tournament matches
- **otp_verification** - OTP storage for email verification

### Database Connection
- **Host**: localhost
- **User**: gemao_user
- **Password**: password
- **Database**: gemao_db (auto-created on startup)

## Authentication & Authorization

### Authentication Flow
1. User registers with email
2. OTP sent to email for verification
3. User logs in with username/password
4. Session created with user_id, user_name, user_role
5. Session expires after 30 minutes of inactivity

### Role-Based Access Control
- **User**: Regular player with access to games and leaderboards
- **Admin**: Full system access including user/game management

### Key Functions
- `login_required` - Decorator for protected routes
- `admin_required` - Decorator for admin-only routes
- `check_password_hash()` - Secure password verification

## Key Features

### User Management
- Registration with email OTP verification
- Profile customization
- Password validation (8+ chars, uppercase, lowercase, digit, special char)
- Duplicate email/username detection

### Authentication
- Session-based with auto-timeout
- Secure password hashing (werkzeug.security)
- HTTPONLY cookies
- CSRF protection ready

### Game System
- 10 Pygame-based mini-games
- Score submission and tracking
- Per-game maximum score enforcement
- Game access control per user

### Leaderboards
- Global ranking system
- Per-game leaderboards
- Top scores display
- Score history

### Admin Features
- User CRUD operations
- Add new games dynamically
- OTP-based user addition
- System statistics dashboard

### Email Integration
- OTP generation and verification
- Email sending via Gmail SMTP
- 10-minute OTP expiry
- Rate limiting on OTP resend

## Security Features

1. **Password Security**
   - Hashing with werkzeug.security
   - Strong password requirements
   - Check against dictionary attacks

2. **Session Security**
   - HTTPONLY cookies
   - Secure flag for production
   - 30-minute timeout
   - CSRF protection ready

3. **Data Validation**
   - Email format validation
   - Input sanitization
   - SQL injection prevention (parameterized queries)
   - CORS headers ready

4. **Access Control**
   - Role-based decorators
   - Route-level authentication
   - Unauthorized access handling

## Configuration & Deployment

### Environment Variables
- `FLASK_ENV` - development/production
- `SECRET_KEY` - Session secret
- `MAIL_USERNAME` - Gmail address
- `MAIL_PASSWORD` - Gmail app password
- Database credentials (host, user, password)

### Running the Application

**Development**:
```bash
python app.py
```

**Production**:
```bash
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Default Test Users

| Username | Password | Role |
|----------|----------|------|
| admin | admin_password | Admin |
| user | user_password | User |

## Technologies Used

- **Web Framework**: Flask 2.3.3
- **Database**: MySQL with mysql-connector-python
- **Game Engine**: Pygame 2.5.2
- **Email**: Flask-Mail
- **Testing**: pytest
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap

## Project Conventions

### Code Style
- PEP 8 compliant
- Docstrings for public methods
- Type hints recommended
- Clear variable naming

### Database Queries
- Always use `get_db_connection()` from db.py
- Close connections after use
- Use parameterized queries
- Handle exceptions with try-except

### Templates
- Extend base.html for consistency
- Use Jinja2 template language
- Follow Naruto theme styling
- Responsive Bootstrap grid

## Troubleshooting

### Common Issues
1. **MySQL Connection Failed** - Ensure MySQL is running
2. **Port 5000 in Use** - Use `flask run --port 5001`
3. **Module Not Found** - Run `pip install -r requirements.txt`
4. **Database Errors** - Check db.py credentials
5. **Email Send Failed** - Verify Gmail app password

## Testing

Run tests with:
```bash
pytest tests/
```

Test files included:
- test_models.py - Model class testing
- test_utils.py - Utility function testing
- test_naruto_run.py - Game logic testing

## Maintenance

### Regular Tasks
- Monitor database size
- Backup user data
- Review error logs
- Update dependencies quarterly

### Performance Optimization
- Database indexing on frequently queried columns
- Template caching in production
- Static file compression
- Database connection pooling

## Future Enhancements

- OAuth2 authentication
- Two-factor authentication
- WebSocket for real-time notifications
- Mobile app version
- Advanced tournament system
- Achievement/badge system
- Social features (friends, messaging)
- Advanced analytics

---

For setup instructions, see STARTUP_GUIDE.md
For architecture details, see copilot-instructions.md
