# NinjaVerse Flask - Developer Quick Reference

## Quick Start (60 seconds)

```bash
# 1. Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# 2. Start MySQL server
# Start XAMPP or your MySQL service

# 3. Run the app
python app.py

# 4. Open browser
# http://localhost:5000
```

## Default Users
- **Admin**: admin / admin_password
- ****:  / _password  
- **User**: user / user_password

---

## Common Development Tasks

### Adding a New Route
```python
from . import your_bp

@your_bp.route('/new-route', methods=['GET', 'POST'])
@login_required
def new_route():
    return render_template('your_template.html')
```

### Database Query Pattern
```python
from MyFlaskapp.db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
result = cursor.fetchone()
conn.close()
```

### Adding Flash Messages
```python
from MyFlaskapp.utils import Alert_Success, Alert_Fail

Alert_Success('Operation successful!')
Alert_Fail('Something went wrong!')
```

### Email/OTP
```python
from MyFlaskapp.utils import generate_otp, send_otp_email, store_otp, verify_otp

otp = generate_otp()
store_otp(email, otp)
send_otp_email(email, otp)
# User submits OTP
if verify_otp(email, otp):
    # OTP is valid
```

### Admin-Only Route
```python
@admin_bp.route('/admin-only')
@login_required
@admin_required
def admin_function():
    pass
```

---

## Project Structure Quick Guide

```
MyFlaskapp/
├── __init__.py          ← Factory pattern: create_app()
├── db.py                ← Database functions
├── config.py            ← Environment configs
├── utils.py             ← Email, validation, alerts
├── models.py            ← Base classes
│
├── auth/                ← Login, register, profile
├── user/                ← User dashboard
├── admin/               ← Admin panel
├── /             ←  features
├── games/               ← Game management & Pygame games
├── leaderboard/         ← Score ranking
├── tournaments/         ← Tournament system
│
├── templates/           ← HTML files (organized by blueprint)
└── static/              ← Images, sounds, CSS
```

---

## Database Quick Reference

### Connect
```python
from MyFlaskapp.db import get_db_connection
conn = get_db_connection()
```

### Key Tables
- **users** - User accounts
- **leaderboards** - Game scores
- **games** - Game definitions
- **tournaments_tb** - Tournaments
- **matches_tb** - Tournament matches

### Insert
```python
cursor.execute("INSERT INTO table_name (col1, col2) VALUES (%s, %s)", (val1, val2))
conn.commit()
```

### Update
```python
cursor.execute("UPDATE table_name SET col1 = %s WHERE id = %s", (val1, id))
conn.commit()
```

### Query
```python
cursor.execute("SELECT * FROM table_name WHERE condition = %s", (value,))
result = cursor.fetchone()       # Single row
results = cursor.fetchall()      # All rows
```

---

## Session Data

Access session variables:
```python
from flask import session

user_id = session.get('user_id')      # str
user_name = session.get('user_name')  # str
user_role = session.get('user_role')  # 'admin', 'user', ''
```

Debug session:
```
http://localhost:5000/debug/session
```

---

## Common Decorators

```python
@login_required          # User must be logged in
@admin_required         # User must be admin
@app.route('/path')     # Define route
@app.route('/path', methods=['GET', 'POST'])  # HTTP methods
```

---

## Adding a New Game

1. Create game file: `MyFlaskapp/games/my_game.py`
2. Inherit from `GameBase`
3. Implement `update()` and `draw()` methods
4. Return score via print/return
5. Add to database in admin panel or db.py

Example structure:
```python
from .game_base import GameBase

class MyGame(GameBase):
    def __init__(self):
        super().__init__()
        self.score = 0
    
    def update(self):
        # Game logic
        pass
    
    def draw(self):
        # Render to screen
        pass
    
    def run(self):
        # Main loop
        super().run()
        return self.score
```

---

## API Response Patterns

### JSON Response
```python
from flask import jsonify

return jsonify({'success': True, 'message': 'Success', 'data': {...}})
return jsonify({'success': False, 'message': 'Error'}), 400
```

### Redirect
```python
from flask import redirect, url_for

return redirect(url_for('blueprint.route_name'))
```

### Template Render
```python
from flask import render_template

return render_template('template.html', variable=value)
```

---

## Debugging Tips

### Print to Console
```python
print(f"Debug: {variable}")  # Shows in terminal
```

### Check Session
Visit: `http://localhost:5000/debug/session`

### Enable Flask Debug Mode
```bash
export FLASK_ENV=development
flask run
```

### Check Database Connection
```python
conn = get_db_connection()
if conn:
    print("Connected!")
```

---

## File Locations

- **Config**: `MyFlaskapp/config.py`
- **Database**: `MyFlaskapp/db.py`
- **Routes**: `MyFlaskapp/{blueprint}/routes.py`
- **Templates**: `MyFlaskapp/templates/{blueprint}/`
- **Static**: `MyFlaskapp/static/{images|sounds}/`
- **Games**: `MyFlaskapp/games/`

---

## Environment Variables

Create `.env` file in project root:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

---

## Useful Commands

```bash
# Activate environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run app
python app.py
flask run

# Run on different port
flask run --port 5001

# Run in production
export FLASK_ENV=production
gunicorn app:app
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| app.py | Entry point |
| requirements.txt | Dependencies |
| config.py | Environment config |
| db.py | Database functions |
| utils.py | Utilities (email, validation) |
| models.py | Base classes |

---

## Useful Links

- Flask docs: https://flask.palletsprojects.com/
- Jinja2 templates: https://jinja.palletsprojects.com/
- Pygame: https://www.pygame.org/
- MySQL: https://www.mysql.com/

---

## Need Help?

1. Check **SYSTEM_DOCUMENTATION.md** for full details
2. Review **STARTUP_GUIDE.md** for setup issues
3. Check console output for error messages
4. Review test files for usage examples
5. Visit `/debug/session` to check authentication state

---

*Last Updated: 2025*
