# Copilot Instructions for GEMAO Flask App

## Architecture Overview

This Flask application uses the application factory pattern with blueprints for modular organization:
- **auth**: Handles login/logout/profile with session-based authentication
- **user**: User dashboard and functionality
- ****: -specific features with role-based access control
- **Database**: MySQL (`gemao_db`) with `user_tb` table storing user credentials and roles
- **Session Management**: Stores `user_id`, `user_name`, `user_role` for authenticated users

Key structural decisions: Role-based routing redirects users to appropriate dashboards post-login.

## Critical Workflows

### Running the Application
1. Activate virtual environment: `venv\Scripts\activate` (Windows)
2. Set Flask app: `$env:FLASK_APP = "MyFlaskapp"` (PowerShell)
3. Run development server: `flask run`
4. Ensure MySQL server is running with credentials: host=localhost, user=gemao_user, password=password

### Database Setup
- Tables created automatically on app startup via `create_user_table()` in `db.py`
- Default users: '' (role: admin) and 'user' (role: user), 'admin' (role: admin) inserted on first run

## Project-Specific Conventions

### Authentication & Authorization
- Use `login_required` decorator (defined in each blueprint) for protected routes
- Passwords stored hashed using werkzeug.security
- Roles: 'admin' (for admin and  types), 'user'
- Role checks: `if session.get('user_role') != 'admin'` for access control
- Flash messages: Import `Alert_Success`/`Alert_Fail` from `utils.py` for user notifications

### Database Interactions
- Always use `get_db_connection()` from `db.py` - establishes connection and selects `gemao_db`
- Close connections after queries: `conn.close()`
- Use parameterized queries: `cursor.execute(sql, (params,))`

### Templates & Styling
- Extend `base.html` for consistent Naruto-themed UI (Bootstrap + custom CSS)
- Template structure: `templates/{blueprint}/{page}.html`
- Static assets: Images in `static/images/`, sounds in `static/sounds/`

### Code Organization
- Blueprint routes in `{blueprint}/routes.py`
- Shared utilities in `utils.py`
- Database functions in `db.py`

## Examples

**Adding a new protected route:**
```python
@user_bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')
```

**Database query pattern:**
```python
conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM user_tb WHERE user_id = %s", (user_id,))
user = cursor.fetchone()
conn.close()
```

**Role-based redirect in login:**
```python
if session['user_role'] == 'admin':
    return redirect(url_for('admin.admin_dashboard'))
else:
    return redirect(url_for('user.dashboard'))
```</content>
<parameter name="filePath">c:\Users\Administrator\Downloads\GEMAO-FLASK (1)\.github\copilot-instructions.md