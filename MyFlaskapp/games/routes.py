from flask import render_template, session, redirect, url_for, request, flash, current_app
from functools import wraps
from . import games_bp
from MyFlaskapp.db import get_db_connection
import subprocess
import sys
import os
import re
import importlib.util

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def user_role_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'user':
            flash('Access denied. This area is for regular users only.', 'warning')
            return redirect(url_for('admin.admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def get_or_create_game_in_db(game):
    """Find existing game in database or create a new entry."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # First try to find by file_path
        cursor.execute("SELECT id FROM games_tb WHERE file_path = %s", (game['file_path'],))
        result = cursor.fetchone()
        
        if result:
            return result['id']
        
        # If not found, create new entry
        cursor.execute(
            "INSERT INTO games_tb (name, description, file_path) VALUES (%s, %s, %s)",
            (game['name'], game['description'], game['file_path'])
        )
        conn.commit()
        return cursor.lastrowid
        
    except Exception as e:
        print(f"Error creating game in database: {e}")
        return None
    finally:
        conn.close()

def safe_int_convert(value, default=0):
    """Safely convert a value to int, handling empty strings and errors."""
    try:
        if value is None or value == '':
            return default
        return int(value.strip())
    except (ValueError, AttributeError):
        return default

def check_game_access(user_id, game_filename):
    """Check if user has access to play a specific game."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT is_enabled FROM user_scanned_game_access_tb WHERE user_id = %s AND game_filename = %s",
            (user_id, game_filename)
        )
        result = cursor.fetchone()
        conn.close()
        
        # If no record exists, default to enabled (backward compatibility)
        if result is None:
            return True
        return result['is_enabled']
    return True  # Default to enabled if DB connection fails

def scan_games_directory():
    """Scan the games directory and extract metadata from Python game files."""
    games_dir = os.path.dirname(__file__)
    games = []
    
    # List of game files to exclude (utility files, etc.)
    exclude_files = {'__init__.py', 'game_launcher.py', 'game_base.py', 'routes.py'}
    
    for filename in os.listdir(games_dir):
        if filename.endswith('.py') and filename not in exclude_files:
            filepath = os.path.join(games_dir, filename)
            game_info = extract_game_metadata(filepath)
            if game_info:
                games.append(game_info)
    
    return games

def extract_game_metadata(filepath):
    """Extract metadata from a game file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = os.path.basename(filepath)
        
        # Extract game title from various patterns
        title_patterns = [
            r'root\.title\(["\']([^"\']+)["\']\)',
            r'super\(\).__init__\([^)]*title=["\']([^"\']+)["\']',
            r'title=["\']([^"\']+)["\']',
        ]
        
        title = None
        for pattern in title_patterns:
            match = re.search(pattern, content)
            if match:
                title = match.group(1).strip()
                break
        
        # If no title found, use filename
        if not title:
            title = filename.replace('.py', '').replace('_', ' ').title()
        
        # Extract class name
        class_match = re.search(r'class\s+(\w+Game|\w+)', content)
        class_name = class_match.group(1) if class_match else 'UnknownGame'
        
        # Generate description based on filename and title
        description = generate_description_from_title(title, filename)
        
        return {
            'id': filename,  # Use filename as ID
            'name': title,
            'description': description,
            'file_path': f'games/{filename}',  # Relative path for launcher
            'filename': filename,
            'class_name': class_name
        }
        
    except Exception as e:
        print(f"Error extracting metadata from {filepath}: {e}")
        return None

def generate_description_from_title(title, filename):
    """Generate a description based on the game title and filename."""
    # Keywords and their associated descriptions
    descriptions = {
        'typing': 'Test your typing speed in this Naruto-themed typing game.',
        'shuriken': 'Practice your aim with shuriken target practice.',
        'memory': 'Challenge your memory with ninja-themed patterns.',
        'clash': 'Battle against opponents in intense jutsu combat.',
        'cat': 'Help catch ninja cats in this fun mission.',
        'tree': 'Master the art of tree climbing with chakra control.',
        'ramen': 'Serve ramen to hungry ninja customers.',
        'roof': 'Run endlessly across village rooftops.',
        'hand': 'Learn and memorize ninja hand signs.',
        'shadow': 'Test your reflexes with shadow clone training.',
        'sharingan': 'Train your Sharingan to spot the differences.',
        'whack': 'Test your speed with shadow clone whack-a-mole.'
    }
    
    title_lower = title.lower()
    filename_lower = filename.lower()
    
    for keyword, desc in descriptions.items():
        if keyword in title_lower or keyword in filename_lower:
            return desc
    
    # Default description if no keywords match
    return f'Experience the ninja world in {title}.'

@games_bp.route('/')
@login_required
@user_role_required
def games_list():
    # Get games from directory scanning
    games = scan_games_directory()
    
    # Try to get top scores from database for games that exist in database
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        from MyFlaskapp.db import get_top_scores_for_game
        
        # Create a mapping of game filenames to database game IDs
        cursor.execute("SELECT * FROM games_tb")
        db_games = cursor.fetchall()
        game_mapping = {game['file_path']: game for game in db_games}
        
        # Add top scores for games that exist in database
        for game in games:
            if game['file_path'] in game_mapping:
                db_game = game_mapping[game['file_path']]
                game['db_id'] = db_game['id']
                game['top_scores'] = get_top_scores_for_game(db_game['id'], 3)
            else:
                # Try to create database entry for scanned games
                game_db_id = get_or_create_game_in_db(game)
                if game_db_id:
                    game['db_id'] = game_db_id
                    game['top_scores'] = get_top_scores_for_game(game_db_id, 3)
                else:
                    game['db_id'] = None
                    game['top_scores'] = []
        
        conn.close()
    else:
        # If no database connection, set empty top scores
        for game in games:
            game['top_scores'] = []
            game['db_id'] = None
    
    return render_template('games/list.html', games=games)

@games_bp.route('/play/<game_filename>')
@login_required
@user_role_required
def play_game_by_filename(game_filename):
    """Play a game using its filename (for directory-scanned games)."""
    # Check user access to this game
    if not check_game_access(session['user_id'], game_filename):
        flash('Access to this game has been restricted by the administrator.', 'danger')
        return redirect(url_for('games.games_list'))
    
    games = scan_games_directory()
    game = None
    
    for g in games:
        if g['filename'] == game_filename:
            game = g
            break
    
    if not game:
        flash('Game not found.', 'danger')
        return redirect(url_for('games.games_list'))
    
    return render_template('games/play.html', game=game)

@games_bp.route('/launch_game/<game_filename>')
@login_required
@user_role_required
def launch_game_by_filename(game_filename):
    """Launch game using filename and capture score automatically."""
    # Check user access to this game
    if not check_game_access(session['user_id'], game_filename):
        flash('Access to this game has been restricted by the administrator.', 'danger')
        return redirect(url_for('games.games_list'))
    
    games = scan_games_directory()
    game = None
    
    for g in games:
        if g['filename'] == game_filename:
            game = g
            break
    
    if not game:
        flash('Game not found.', 'danger')
        return redirect(url_for('games.games_list'))
    
    try:
        # Get the full game file path
        game_file_path = os.path.join(os.path.dirname(__file__), game_filename)
        
        # Validate game file exists
        if not os.path.exists(game_file_path):
            flash('Game file not found.', 'danger')
            return redirect(url_for('games.games_list'))
        
        # Get the launcher script path
        launcher_path = os.path.join(os.path.dirname(__file__), 'game_launcher.py')
        
        # Execute the game using the launcher
        launcher_result = subprocess.run(
            [sys.executable, launcher_path, game_file_path],
            capture_output=True,
            text=True,
            timeout=current_app.config.get('GAME_TIMEOUT_SECONDS', 300),
            cwd=os.path.dirname(game_file_path),
            shell=False
        )
        
        # Extract score from launcher output
        score = safe_int_convert(launcher_result.stdout)
        
        # Try to submit score if game exists in database
        if score > 0:
            user_id = session['user_id']
            from MyFlaskapp.db import submit_score as db_submit_score
            
            # If game has db_id, use it directly
            if game.get('db_id'):
                if db_submit_score(user_id, game['db_id'], score):
                    flash(f'Game completed! Score: {score}', 'success')
                else:
                    flash('Failed to submit score.', 'danger')
            else:
                # Try to find or create game in database by filename
                game_db_id = get_or_create_game_in_db(game)
                if game_db_id and db_submit_score(user_id, game_db_id, score):
                    flash(f'Game completed! Score: {score}', 'success')
                else:
                    flash(f'Game completed! Score: {score} (Note: Score not saved to leaderboard)', 'warning')
        else:
            flash('Game completed but no valid score was captured.', 'warning')
            
    except subprocess.TimeoutExpired:
        flash('Game timed out after 5 minutes.', 'danger')
    except subprocess.CalledProcessError as e:
        flash(f'Game execution failed: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Error launching game: {str(e)}', 'danger')
    
    return redirect(url_for('games.games_list'))

@games_bp.route('/play/<int:game_id>')
@login_required
@user_role_required
def play_game(game_id):
    conn = get_db_connection()
    game = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM games_tb WHERE id = %s", (game_id,))
        game = cursor.fetchone()
        conn.close()
    if game:
        return render_template('games/play.html', game=game)
    else:
        flash('Game not found.', 'danger')
        return redirect(url_for('games.games_list'))

@games_bp.route('/launch_game/<int:game_id>')
@login_required
@user_role_required
def launch_game(game_id):
    """Launch game using the desktop launcher and capture score automatically."""
    conn = get_db_connection()
    game = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM games_tb WHERE id = %s", (game_id,))
        game = cursor.fetchone()
        conn.close()
    
    if not game:
        flash('Game not found.', 'danger')
        return redirect(url_for('games.games_list'))
    
    try:
        # Get the game file path
        game_file_path = game.get('file_path', '')
        if not game_file_path:
            flash('Game file not specified.', 'danger')
            return redirect(url_for('games.games_list'))
        
        # Validate game file path for security
        from MyFlaskapp.security_utils import validate_game_file_path
        # Extract just the filename if path includes 'games/' prefix
        if game_file_path.startswith('games/'):
            relative_path = game_file_path[6:]  # Remove 'games/' prefix
        else:
            relative_path = game_file_path
        is_valid, result = validate_game_file_path(relative_path)
        if not is_valid:
            flash(f'Invalid game file: {result}', 'danger')
            return redirect(url_for('games.games_list'))
        
        full_path = result  # validated path
        
        # Get the launcher script path
        launcher_path = os.path.join(os.path.dirname(__file__), 'game_launcher.py')
        
        # Execute the game using the launcher
        launcher_result = subprocess.run(
            [sys.executable, launcher_path, full_path],
            capture_output=True,
            text=True,
            timeout=current_app.config.get('GAME_TIMEOUT_SECONDS', 300),
            cwd=os.path.dirname(full_path),
            shell=False
        )
        
        # Extract score from launcher output
        score = safe_int_convert(launcher_result.stdout)
        
        if score > 0:
            user_id = session['user_id']
            from MyFlaskapp.db import submit_score as db_submit_score
            if db_submit_score(user_id, game_id, score):
                flash(f'Game completed! Score: {score}', 'success')
            else:
                flash('Failed to submit score.', 'danger')
        else:
            flash('Game completed but no valid score was captured.', 'warning')
            
    except subprocess.TimeoutExpired:
        flash('Game timed out after 5 minutes.', 'danger')
    except subprocess.CalledProcessError as e:
        flash(f'Game execution failed: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Error launching game: {str(e)}', 'danger')
    
    return redirect(url_for('games.games_list'))

@games_bp.route('/run_game/<int:game_id>')
@login_required
@user_role_required
def run_game(game_id):
    """Execute game as subprocess and capture score (legacy method for console games)."""
    conn = get_db_connection()
    game = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM games_tb WHERE id = %s", (game_id,))
        game = cursor.fetchone()
        conn.close()
    
    if not game:
        flash('Game not found.', 'danger')
        return redirect(url_for('games.games_list'))
    
    try:
        # Get the game file path
        game_file_path = game.get('file_path', '')
        if not game_file_path:
            flash('Game file not specified.', 'danger')
            return redirect(url_for('games.games_list'))
        
        # Validate game file path for security
        from MyFlaskapp.security_utils import validate_game_file_path
        is_valid, result = validate_game_file_path(game_file_path)
        if not is_valid:
            flash(f'Invalid game file: {result}', 'danger')
            return redirect(url_for('games.games_list'))
        
        full_path = result  # validated path
        
        # Execute the game as subprocess with additional security
        result = subprocess.run(
            [sys.executable, full_path],
            capture_output=True,
            text=True,
            timeout=current_app.config.get('GAME_TIMEOUT_SECONDS', 300),
            cwd=os.path.dirname(full_path),  # Run in game directory
            shell=False  # Prevent shell injection
        )
        
        # Safely extract score from stdout
        score = safe_int_convert(result.stdout)
        
        if score > 0:
            user_id = session['user_id']
            from MyFlaskapp.db import submit_score as db_submit_score
            if db_submit_score(user_id, game_id, score):
                flash(f'Game completed! Score: {score}', 'success')
            else:
                flash('Failed to submit score.', 'danger')
        else:
            flash('Game completed but no valid score was returned.', 'warning')
            
    except subprocess.TimeoutExpired:
        flash('Game timed out after 5 minutes.', 'danger')
    except subprocess.CalledProcessError as e:
        flash(f'Game execution failed: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Error running game: {str(e)}', 'danger')
    
    return redirect(url_for('games.games_list'))

@games_bp.route('/submit_score/<int:game_id>', methods=['POST'])
@login_required
@user_role_required
def submit_score(game_id):
    score = request.form.get('score', type=int)
    user_id = session['user_id']
    from MyFlaskapp.db import submit_score as db_submit_score
    if db_submit_score(user_id, game_id, score):
        flash('Score submitted!', 'success')
    else:
        flash('Failed to submit score.', 'danger')
    return redirect(url_for('games.games_list'))
