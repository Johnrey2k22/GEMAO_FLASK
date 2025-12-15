from flask import render_template, session, redirect, url_for, jsonify, request
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
    view_type = request.args.get('view', 'personal')  # 'personal' or 'global'
    conn = get_db_connection()
    user_scores = []
    global_scores = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get current user's database ID
        user_id = session.get('user_id')
        cursor.execute("SELECT id FROM user_tb WHERE user_id = %s", (user_id,))
        user_result = cursor.fetchone()
        user_db_id = user_result['id'] if user_result else None
        
        # Get user's own scores
        if user_db_id:
            cursor.execute("""
                SELECT l.score, g.name as game_name, u.username, l.created_at as date_played
                FROM scores_tb l
                JOIN games_tb g ON l.game_id = g.id
                JOIN user_tb u ON l.user_id = u.id
                WHERE l.user_id = %s
                ORDER BY l.score DESC
            """, (user_db_id,))
            user_scores = cursor.fetchall()
        
        # Get global scores (all users)
        cursor.execute("""
            SELECT l.score, g.name as game_name, u.username, l.created_at as date_played
            FROM scores_tb l
            JOIN games_tb g ON l.game_id = g.id
            JOIN user_tb u ON l.user_id = u.id
            ORDER BY l.score DESC
            LIMIT 50
        """)
        global_scores = cursor.fetchall()
        
        print(f"DEBUG: User scores: {len(user_scores)}, Global scores: {len(global_scores)}")
        conn.close()
    else:
        print("DEBUG: Failed to connect to database")
    
    return render_template('leaderboard/leaderboard.html', 
                         user_scores=user_scores, 
                         global_scores=global_scores, 
                         view_type=view_type)

@leaderboard_bp.route('/api/data')
@login_required
def leaderboard_api():
    """API endpoint for real-time leaderboard data"""
    view_type = request.args.get('view', 'personal')  # 'personal' or 'global'
    conn = get_db_connection()
    user_scores = []
    global_scores = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get current user's database ID
        user_id = session.get('user_id')
        cursor.execute("SELECT id FROM user_tb WHERE user_id = %s", (user_id,))
        user_result = cursor.fetchone()
        user_db_id = user_result['id'] if user_result else None
        
        # Get user's own scores
        if user_db_id:
            cursor.execute("""
                SELECT l.score, g.name as game_name, u.username, l.created_at as date_played
                FROM scores_tb l
                JOIN games_tb g ON l.game_id = g.id
                JOIN user_tb u ON l.user_id = u.id
                WHERE l.user_id = %s
                ORDER BY l.score DESC
            """, (user_db_id,))
            user_scores = cursor.fetchall()
        
        # Get global scores (all users)
        cursor.execute("""
            SELECT l.score, g.name as game_name, u.username, l.created_at as date_played
            FROM scores_tb l
            JOIN games_tb g ON l.game_id = g.id
            JOIN user_tb u ON l.user_id = u.id
            ORDER BY l.score DESC
            LIMIT 50
        """)
        global_scores = cursor.fetchall()
        conn.close()
    
    # Convert datetime objects to strings for JSON serialization
    for score in user_scores:
        if score.get('date_played'):
            score['date_played'] = score['date_played'].strftime('%Y-%m-%d %H:%M:%S')
    
    for score in global_scores:
        if score.get('date_played'):
            score['date_played'] = score['date_played'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        'user_scores': user_scores,
        'global_scores': global_scores,
        'view_type': view_type
    })

@leaderboard_bp.route('/game/<int:game_id>')
@login_required
def game_leaderboard(game_id):
    """Display leaderboard for a specific game"""
    view_type = request.args.get('view', 'personal')  # 'personal' or 'global'
    conn = get_db_connection()
    game = None
    user_scores = []
    global_scores = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM games_tb WHERE id = %s", (game_id,))
        game = cursor.fetchone()
        
        if game:
            # Get current user's database ID
            user_id = session.get('user_id')
            cursor.execute("SELECT id FROM user_tb WHERE user_id = %s", (user_id,))
            user_result = cursor.fetchone()
            user_db_id = user_result['id'] if user_result else None
            
            # Get user's scores for this game
            if user_db_id:
                cursor.execute("""
                    SELECT l.leaderboard_id, l.score, u.username, l.created_at as date_played
                    FROM scores_tb l
                    JOIN user_tb u ON l.user_id = u.id
                    WHERE l.game_id = %s AND l.user_id = %s
                    ORDER BY l.score DESC
                """, (game_id, user_db_id))
                user_scores = cursor.fetchall()
            
            # Get global scores for this game
            cursor.execute("""
                SELECT l.leaderboard_id, l.score, u.username, l.created_at as date_played
                FROM scores_tb l
                JOIN user_tb u ON l.user_id = u.id
                WHERE l.game_id = %s
                ORDER BY l.score DESC
            """, (game_id,))
            global_scores = cursor.fetchall()
        
        conn.close()
    
    if not game:
        return redirect(url_for('leaderboard.leaderboard'))
    
    return render_template('leaderboard/game_leaderboard.html', 
                         game=game, 
                         user_scores=user_scores,
                         global_scores=global_scores,
                         view_type=view_type)

@leaderboard_bp.route('/game/<int:game_id>/api/data')
@login_required
def game_leaderboard_api(game_id):
    """API endpoint for real-time game-specific leaderboard data"""
    view_type = request.args.get('view', 'personal')  # 'personal' or 'global'
    conn = get_db_connection()
    game = None
    user_scores = []
    global_scores = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name FROM games_tb WHERE id = %s", (game_id,))
        game = cursor.fetchone()
        
        if game:
            # Get current user's database ID
            user_id = session.get('user_id')
            cursor.execute("SELECT id FROM user_tb WHERE user_id = %s", (user_id,))
            user_result = cursor.fetchone()
            user_db_id = user_result['id'] if user_result else None
            
            # Get user's scores for this game
            if user_db_id:
                cursor.execute("""
                    SELECT l.leaderboard_id, l.score, u.username, l.created_at as date_played
                    FROM scores_tb l
                    JOIN user_tb u ON l.user_id = u.id
                    WHERE l.game_id = %s AND l.user_id = %s
                    ORDER BY l.score DESC
                """, (game_id, user_db_id))
                user_scores = cursor.fetchall()
            
            # Get global scores for this game
            cursor.execute("""
                SELECT l.leaderboard_id, l.score, u.username, l.created_at as date_played
                FROM scores_tb l
                JOIN user_tb u ON l.user_id = u.id
                WHERE l.game_id = %s
                ORDER BY l.score DESC
            """, (game_id,))
            global_scores = cursor.fetchall()
        
        conn.close()
    
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Convert datetime objects to strings for JSON serialization
    for score in user_scores:
        if score.get('date_played'):
            score['date_played'] = score['date_played'].strftime('%Y-%m-%d %H:%M:%S')
    
    for score in global_scores:
        if score.get('date_played'):
            score['date_played'] = score['date_played'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        'user_scores': user_scores,
        'global_scores': global_scores,
        'view_type': view_type
    })