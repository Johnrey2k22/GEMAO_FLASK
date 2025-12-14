from flask import render_template, session, redirect, url_for, jsonify
from functools import wraps
from . import leaderboard_bp
from MyFlaskapp.db import get_db_connection, get_all_scores_for_game

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@leaderboard_bp.route('/')
@login_required
def leaderboard():
    conn = get_db_connection()
    scores = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT l.score, g.name as game_name, u.username, l.created_at as date_played
            FROM scores_tb l
            JOIN games_tb g ON l.game_id = g.id
            JOIN user_tb u ON l.user_id = u.id
            ORDER BY l.score DESC
            LIMIT 50
        """)
        scores = cursor.fetchall()
        print(f"DEBUG: Database query returned {len(scores)} scores")
        for score in scores:
            print(f"DEBUG: Username: {score.get('username')}, Game: {score.get('game_name')}, Score: {score.get('score')}, Date: {score.get('date_played')}")
        conn.close()
    else:
        print("DEBUG: Failed to connect to database")
    print(f"DEBUG: Passing {len(scores)} scores to template")
    return render_template('leaderboard/leaderboard.html', scores=scores)

@leaderboard_bp.route('/api/data')
@login_required
def leaderboard_api():
    """API endpoint for real-time leaderboard data"""
    conn = get_db_connection()
    scores = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT l.score, g.name as game_name, u.username, l.created_at as date_played
            FROM scores_tb l
            JOIN games_tb g ON l.game_id = g.id
            JOIN user_tb u ON l.user_id = u.id
            ORDER BY l.score DESC
            LIMIT 50
        """)
        scores = cursor.fetchall()
        conn.close()
    
    # Convert datetime objects to strings for JSON serialization
    for score in scores:
        if score['date_played']:
            score['date_played'] = score['date_played'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify(scores)

@leaderboard_bp.route('/game/<int:game_id>')
@login_required
def game_leaderboard(game_id):
    """Display leaderboard for a specific game"""
    conn = get_db_connection()
    game = None
    scores = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM games_tb WHERE id = %s", (game_id,))
        game = cursor.fetchone()
        if game:
            scores = get_all_scores_for_game(game_id)
        conn.close()
    
    if not game:
        return redirect(url_for('leaderboard.leaderboard'))
    
    return render_template('leaderboard/game_leaderboard.html', game=game, scores=scores)

@leaderboard_bp.route('/game/<int:game_id>/api/data')
@login_required
def game_leaderboard_api(game_id):
    """API endpoint for real-time game-specific leaderboard data"""
    conn = get_db_connection()
    game = None
    scores = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name FROM games_tb WHERE id = %s", (game_id,))
        game = cursor.fetchone()
        if game:
            scores = get_all_scores_for_game(game_id)
        conn.close()
    
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Convert datetime objects to strings for JSON serialization
    for score in scores:
        if score.get('date_played'):
            score['date_played'] = score['date_played'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify(scores)