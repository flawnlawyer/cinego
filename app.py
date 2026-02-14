from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
import os
from datetime import datetime, date
import random
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['DATABASE'] = os.path.join(app.instance_path, 'cinego.db')

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)


from tmdb_client import TMDBClient

# ... existing imports ...


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables and sample data from TMDB"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create movies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            rating REAL,
            image_url TEXT,
            description TEXT,
            is_trending BOOLEAN DEFAULT 0,
            view_count INTEGER DEFAULT 0,
            video_url TEXT,
            trailer_url TEXT
        )
    ''')
    
    # Create series table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            rating REAL,
            image_url TEXT,
            description TEXT,
            seasons INTEGER DEFAULT 1,
            video_url TEXT,
            trailer_url TEXT
        )
    ''')
    
    # Create chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            is_bot BOOLEAN DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create watch time tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watch_time (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            date DATE DEFAULT CURRENT_DATE,
            minutes_watched INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
    ''')
    
    # Create user preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            favorite_genres TEXT,
            last_genre_watched TEXT,
            total_watch_time INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Check if data already exists to avoid refetching
    cursor.execute('SELECT COUNT(*) FROM movies')
    if cursor.fetchone()[0] == 0:
        print("Fetching data from TMDB...")
        
        all_movies = {}
        
        # Helper to process and add movies
        def add_movies(movie_list):
            for m in movie_list:
                all_movies[m['id']] = m
        
        # Fetch multiple pages for better variety
        print("Fetching Trending...")
        for page in range(1, 4):
            add_movies(TMDBClient.fetch_trending_movies(page=page))
            
        print("Fetching Top Rated...")
        for page in range(1, 3):
            add_movies(TMDBClient.fetch_top_rated_movies(page=page))
            
        print("Fetching Now Playing...")
        for page in range(1, 3):
            add_movies(TMDBClient.fetch_now_playing_movies(page=page))
            
        print("Fetching Action & Comedy...")
        add_movies(TMDBClient.fetch_action_movies(page=1))
        add_movies(TMDBClient.fetch_comedy_movies(page=1))
        
        # Sort by popularity to find the "best" ones to get trailers for
        sorted_movies = sorted(all_movies.values(), key=lambda x: x.get('view_count', 0), reverse=True)
        
        # Fetch trailers for top 20 movies to keep startup time reasonable but responsive
        print("Fetching trailers for top movies...")
        count = 0
        for movie_data in sorted_movies:
            if count < 20: 
                video_data = TMDBClient.fetch_movie_videos(movie_data['id'])
                if video_data:
                    # We store the URL in trailer_url mostly, but could use video_url if it's a "clip" acting as a movie
                    movie_data['trailer_url'] = video_data['url']
                count += 1
            
            # Insert into DB
            cursor.execute('''
                INSERT OR IGNORE INTO movies (id, title, year, genre, rating, image_url, description, is_trending, view_count, video_url, trailer_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                movie_data['id'], 
                movie_data['title'], 
                movie_data['year'], 
                movie_data['genre'], 
                movie_data['rating'], 
                movie_data['image_url'], 
                movie_data['description'], 
                movie_data.get('is_trending', 0), 
                movie_data['view_count'], 
                movie_data['video_url'], 
                movie_data.get('trailer_url', '')
            ))
            
        # Fetch series (more pages)
        print("Fetching Series...")
        all_series = []
        for page in range(1, 4):
            all_series.extend(TMDBClient.fetch_popular_series(page=page))

        print(f"Fetching videos for {len(all_series)} series...")
        for s in all_series:
            # Fetch video for ALL series as requested
            video_data = TMDBClient.fetch_series_videos(s['id'])
            trailer_url = video_data['url'] if video_data else ''

            cursor.execute('''
                INSERT OR IGNORE INTO series (id, title, year, genre, rating, image_url, description, seasons, video_url, trailer_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                s.get('id'), # Use TMDB ID
                s['title'], 
                s['year'], 
                s['genre'], 
                s['rating'], 
                s['image_url'], 
                s['description'], 
                s['seasons'],
                '', # video_url (empty for now)
                trailer_url
            ))
            
        print(f"Database initialized with {len(all_movies)} movies and {len(all_series)} series data.")
        
    conn.commit()
    conn.close()

# Initialize database on first run
with app.app_context():
    init_db()

# ================== CINEBOT AI ENGINE ==================

class CineBot:
    """Smart movie recommendation chatbot"""
    
    # Genre mappings for mood-based recommendations
    MOOD_GENRE_MAP = {
        'happy': ['Comedy', 'Adventure', 'Fantasy'],
        'sad': ['Drama', 'Romance'],
        'excited': ['Action', 'Sci-Fi', 'Thriller'],
        'scared': ['Horror', 'Mystery', 'Thriller'],
        'romantic': ['Romance', 'Drama'],
        'adventurous': ['Adventure', 'Action', 'Fantasy'],
        'thoughtful': ['Drama', 'Sci-Fi', 'Mystery'],
        'relaxed': ['Comedy', 'Romance', 'Adventure'],
        'tense': ['Thriller', 'Horror', 'Crime']
    }
    
    # Genre keywords for detection
    GENRE_KEYWORDS = {
        'action': 'Action',
        'comedy': 'Comedy',
        'drama': 'Drama',
        'horror': 'Horror',
        'scifi': 'Sci-Fi',
        'sci-fi': 'Sci-Fi',
        'science fiction': 'Sci-Fi',
        'romance': 'Romance',
        'thriller': 'Thriller',
        'mystery': 'Mystery',
        'adventure': 'Adventure',
        'fantasy': 'Fantasy',
        'crime': 'Crime',
        'war': 'War'
    }
    
    # Personality responses
    GREETINGS = [
        "Hey there, movie lover! 🎬 What can I help you find today?",
        "Welcome back to CINEGO! Ready to discover something amazing?",
        "Hi! I'm CineBot, your personal movie guide. What's your vibe today?",
        "Hello! Looking for your next favorite movie? I'm here to help! 🍿"
    ]
    
    WATCH_TIME_WARNINGS = {
        120: "You've watched 2 hours today. Staying entertained? 😊",
        180: "3 hours of cinema today! Even heroes need breaks. Consider a stretch? 🧘",
        240: "4 hours! Your dedication is impressive, but remember to rest your eyes. 👀",
        300: "5 hours! Time flies when you're having fun, but maybe grab some water? 💧"
    }
    
    @staticmethod
    def detect_intent(message):
        """Detect user intent from message"""
        message = message.lower()
        
        # Greetings
        if any(word in message for word in ['hi', 'hello', 'hey', 'greetings']):
            return 'greeting'
        
        # Recommendations
        if any(word in message for word in ['recommend', 'suggest', 'find', 'looking for', 'want to watch', 'show me']):
            return 'recommend'
        
        # Mood-based
        if any(word in message for word in ['feel', 'mood', 'feeling', 'vibe']):
            return 'mood'
        
        # Watch time
        if any(word in message for word in ['watched', 'watch time', 'how long', 'how much']):
            return 'watch_time'
        
        # Help
        if any(word in message for word in ['help', 'what can you do', 'commands']):
            return 'help'
        
        return 'general'
    
    @staticmethod
    def extract_genre(message):
        """Extract genre from message"""
        message = message.lower()
        for keyword, genre in CineBot.GENRE_KEYWORDS.items():
            if keyword in message:
                return genre
        return None
    
    @staticmethod
    def extract_mood(message):
        """Extract mood from message"""
        message = message.lower()
        for mood in CineBot.MOOD_GENRE_MAP.keys():
            if mood in message:
                return mood
        return None
    
    @staticmethod
    def get_recommendations(genre=None, mood=None, user_id=None, limit=3):
        """Get movie recommendations based on criteria"""
        conn = get_db()
        cursor = conn.cursor()
        
        # Determine genres to search
        genres_to_search = []
        if genre:
            genres_to_search = [genre]
        elif mood and mood in CineBot.MOOD_GENRE_MAP:
            genres_to_search = CineBot.MOOD_GENRE_MAP[mood]
        
        # Build query
        if genres_to_search:
            placeholders = ','.join(['?' for _ in genres_to_search])
            query = f'''
                SELECT * FROM movies 
                WHERE genre IN ({placeholders})
                ORDER BY rating DESC, view_count DESC
                LIMIT ?
            '''
            cursor.execute(query, genres_to_search + [limit])
        else:
            # Random top-rated movies
            cursor.execute('''
                SELECT * FROM movies 
                ORDER BY rating DESC, view_count DESC
                LIMIT ?
            ''', (limit,))
        
        movies = cursor.fetchall()
        conn.close()
        return movies
    
    @staticmethod
    def get_watch_time_today(user_id):
        """Get total watch time for user today"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(minutes_watched) 
            FROM watch_time 
            WHERE user_id = ? AND date = ?
        ''', (user_id, date.today()))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result[0] else 0
    
    @staticmethod
    def update_watch_time(user_id, movie_id, minutes):
        """Update user's watch time"""
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if entry exists for today
        cursor.execute('''
            SELECT id, minutes_watched FROM watch_time
            WHERE user_id = ? AND movie_id = ? AND date = ?
        ''', (user_id, movie_id, date.today()))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            cursor.execute('''
                UPDATE watch_time 
                SET minutes_watched = minutes_watched + ?
                WHERE id = ?
            ''', (minutes, existing[0]))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO watch_time (user_id, movie_id, date, minutes_watched)
                VALUES (?, ?, ?, ?)
            ''', (user_id, movie_id, date.today(), minutes))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_watch_time_warning(total_minutes):
        """Get appropriate warning based on watch time"""
        for threshold, warning in sorted(CineBot.WATCH_TIME_WARNINGS.items()):
            if total_minutes >= threshold and total_minutes < threshold + 30:
                return warning
        return None
    
    @staticmethod
    def save_chat_message(user_id, message, is_bot=False):
        """Save chat message to history"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (user_id, message, is_bot)
            VALUES (?, ?, ?)
        ''', (user_id, message, is_bot))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_chat_history(user_id, limit=20):
        """Get recent chat history"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message, is_bot, timestamp
            FROM chat_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        messages = cursor.fetchall()
        conn.close()
        return list(reversed(messages))
    
    @staticmethod
    def generate_response(message, user_id):
        """Generate bot response based on message"""
        intent = CineBot.detect_intent(message)
        
        # Greeting
        if intent == 'greeting':
            return random.choice(CineBot.GREETINGS)
        
        # Help
        if intent == 'help':
            return """I can help you with:
🎬 Movie recommendations (by genre or mood)
⏱️ Track your watch time
💡 Suggest what to watch next

Try asking: "Recommend an action movie" or "I feel happy, what should I watch?"
"""
        
        # Watch time
        if intent == 'watch_time':
            total_minutes = CineBot.get_watch_time_today(user_id)
            hours = total_minutes // 60
            mins = total_minutes % 60
            response = f"You've watched {hours}h {mins}m today. "
            
            warning = CineBot.get_watch_time_warning(total_minutes)
            if warning:
                response += warning
            else:
                response += "Keep enjoying! 🍿"
            
            return response
        
        # Recommendations
        if intent in ['recommend', 'mood']:
            genre = CineBot.extract_genre(message)
            mood = CineBot.extract_mood(message)
            
            movies = CineBot.get_recommendations(genre, mood, user_id, limit=3)
            
            if not movies:
                return "Hmm, I couldn't find movies matching that. Try asking for Action, Drama, Sci-Fi, or tell me your mood!"
            
            # Build response
            if genre:
                response = f"Perfect! Here are top {genre} movies for you:\n\n"
            elif mood:
                response = f"Feeling {mood}? These should hit the spot:\n\n"
            else:
                response = "Here are some top picks for you:\n\n"
            
            for i, movie in enumerate(movies, 1):
                response += f"{i}. **{movie['title']}** ({movie['year']}) ⭐ {movie['rating']}/10\n"
                response += f"   {movie['description']}\n\n"
            
            response += "Click any movie to start watching! 🎬"
            return response
        
        # General conversation
        return "I'm CineBot! Ask me to recommend movies, check your watch time, or just tell me what mood you're in! 😊"

# ================== END CINEBOT AI ENGINE ==================

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Homepage with all movies and series"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all movies
    cursor.execute('SELECT * FROM movies ORDER BY view_count DESC')
    all_movies = cursor.fetchall()
    
    # Get trending movies
    cursor.execute('SELECT * FROM movies WHERE is_trending = 1 ORDER BY view_count DESC LIMIT 10')
    trending = cursor.fetchall()
    
    # Get latest movies
    cursor.execute('SELECT * FROM movies ORDER BY id DESC LIMIT 10')
    latest = cursor.fetchall()
    
    # Get series
    cursor.execute('SELECT * FROM series ORDER BY rating DESC')
    series = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                         all_movies=all_movies,
                         trending=trending,
                         latest=latest,
                         series=series,
                         username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                         (username, email, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/movies')
@login_required
def movies():
    """Movies page"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies ORDER BY rating DESC')
    all_movies = cursor.fetchall()
    conn.close()
    
    return render_template('movies.html', movies=all_movies, username=session.get('username'))

@app.route('/series')
@login_required
def series_page():
    """Series page"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM series ORDER BY rating DESC')
    all_series = cursor.fetchall()
    conn.close()
    
    return render_template('series.html', series=all_series, username=session.get('username'))

@app.route('/movie/<int:movie_id>')
@login_required
def movie_detail(movie_id):
    """Movie detail page"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
    movie = cursor.fetchone()
    
    # Increment view count
    cursor.execute('UPDATE movies SET view_count = view_count + 1 WHERE id = ?', (movie_id,))
    conn.commit()
    conn.close()
    
    if not movie:
        flash('Movie not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('movie_detail.html', movie=movie, username=session.get('username'))

@app.route('/series/<int:series_id>')
@login_required
def series_detail(series_id):
    """Series detail page"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM series WHERE id = ?', (series_id,))
    series = cursor.fetchone()
    conn.close()
    
    if not series:
        flash('Series not found', 'error')
        return redirect(url_for('series_page'))
    
    return render_template('series_detail.html', series=series, username=session.get('username'))

@app.route('/watch/series/<int:series_id>')
@login_required
def watch_series(series_id):
    """Watch series - Video player page"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM series WHERE id = ?', (series_id,))
    series = cursor.fetchone()
    
    # Get recommended series
    cursor.execute('SELECT * FROM series WHERE genre = ? AND id != ? LIMIT 6', (series['genre'], series_id))
    recommended = cursor.fetchall()
    
    conn.close()
    
    if not series:
        flash('Series not found', 'error')
        return redirect(url_for('series_page'))
    
    return render_template('watch_series.html', series=series, recommended=recommended, username=session.get('username'))

@app.route('/watch/<int:movie_id>')
@login_required
def watch_movie(movie_id):
    """Watch movie - Video player page"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
    movie = cursor.fetchone()
    
    # Increment view count
    cursor.execute('UPDATE movies SET view_count = view_count + 1 WHERE id = ?', (movie_id,))
    conn.commit()
    
    # Get recommended movies (same genre)
    cursor.execute('SELECT * FROM movies WHERE genre = ? AND id != ? LIMIT 6', (movie['genre'], movie_id))
    recommended = cursor.fetchall()
    
    conn.close()
    
    if not movie:
        flash('Movie not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('watch.html', movie=movie, recommended=recommended, username=session.get('username'))

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    """CineBot chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        user_id = session.get('user_id')
        
        # Save user message
        CineBot.save_chat_message(user_id, user_message, is_bot=False)
        
        # Generate bot response
        bot_response = CineBot.generate_response(user_message, user_id)
        
        # Save bot response
        CineBot.save_chat_message(user_id, bot_response, is_bot=True)
        
        # Check watch time and add warning if needed
        total_watch_time = CineBot.get_watch_time_today(user_id)
        watch_warning = CineBot.get_watch_time_warning(total_watch_time)
        
        return jsonify({
            'response': bot_response,
            'watch_warning': watch_warning,
            'success': True
        })
    
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': 'Something went wrong'}), 500

@app.route('/chat/history')
@login_required
def chat_history():
    """Get chat history"""
    try:
        user_id = session.get('user_id')
        messages = CineBot.get_chat_history(user_id, limit=50)
        
        history = []
        for msg in messages:
            history.append({
                'message': msg['message'],
                'is_bot': bool(msg['is_bot']),
                'timestamp': msg['timestamp']
            })
        
        return jsonify({'history': history, 'success': True})
    
    except Exception as e:
        print(f"Chat history error: {str(e)}")
        return jsonify({'error': 'Failed to load history'}), 500

@app.route('/update_watch_time', methods=['POST'])
@login_required
def update_watch_time():
    """Update user watch time"""
    try:
        data = request.get_json()
        movie_id = data.get('movie_id')
        minutes = data.get('minutes', 0)
        
        user_id = session.get('user_id')
        CineBot.update_watch_time(user_id, movie_id, minutes)
        
        # Get total watch time today
        total_minutes = CineBot.get_watch_time_today(user_id)
        warning = CineBot.get_watch_time_warning(total_minutes)
        
        return jsonify({
            'success': True,
            'total_minutes': total_minutes,
            'warning': warning
        })
    
    except Exception as e:
        print(f"Watch time update error: {str(e)}")
        return jsonify({'error': 'Failed to update watch time'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
