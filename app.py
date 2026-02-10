from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['DATABASE'] = os.path.join(app.instance_path, 'cinego.db')

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables and sample data"""
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            rating REAL,
            image_url TEXT,
            description TEXT,
            seasons INTEGER DEFAULT 1
        )
    ''')
    
    # Insert sample movies
    sample_movies = [
        ('The Last Stand', 2023, 'Action', 8.5, 'https://image.tmdb.org/t/p/w500/1E5baAaEse26fej7uHcjOgEE2t2.jpg', 'An epic action thriller', 1, 1250, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('Midnight Echo', 2024, 'Drama', 7.8, 'https://image.tmdb.org/t/p/w500/qNBAXBIQlnOThrVvA6mA2B5ggV6.jpg', 'A gripping drama', 1, 980, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('Shadow Protocol', 2023, 'Thriller', 8.2, 'https://image.tmdb.org/t/p/w500/sv1xJUazXeYqALzczSZ3O6nkH75.jpg', 'High-stakes espionage', 1, 1411, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('Neon Dreams', 2024, 'Sci-Fi', 9.0, 'https://image.tmdb.org/t/p/w500/cinER0ESG0eJ49kXlExM0MEWGxW.jpg', 'Futuristic adventure', 1, 2100, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('The Forgotten', 2023, 'Horror', 7.5, 'https://image.tmdb.org/t/p/w500/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg', 'Supernatural horror', 0, 650, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('Ocean Rise', 2024, 'Adventure', 8.7, 'https://image.tmdb.org/t/p/w500/kHlX3oqdD4VGaLpB8O78M8DXTM5.jpg', 'Maritime epic', 1, 1800, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('Silent Hills', 2023, 'Mystery', 7.9, 'https://image.tmdb.org/t/p/w500/wWba3TaojhK7NdycRhoQpsG0FaH.jpg', 'Mystery thriller', 0, 720, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('Velocity', 2024, 'Action', 8.3, 'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg', 'High-speed action', 1, 1560, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('Eternal Spring', 2023, 'Romance', 7.6, 'https://image.tmdb.org/t/p/w500/yDHYTfA3R0jFYba16jBB1ef8oIt.jpg', 'Love story', 0, 890, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('Dark Matter', 2024, 'Sci-Fi', 8.9, 'https://image.tmdb.org/t/p/w500/aWeKITRFbbwY8txG5uCj4rMCfSP.jpg', 'Space odyssey', 1, 2350, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('The Heist', 2023, 'Crime', 8.1, 'https://image.tmdb.org/t/p/w500/4m1Au3YkjqsxF8iwQy0fPYSxE0h.jpg', 'Master thieves', 0, 1100, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('Phoenix Rising', 2024, 'Fantasy', 8.6, 'https://image.tmdb.org/t/p/w500/xDMIl84Qo5Tsu62c9DGWhmPI67A.jpg', 'Mythical journey', 1, 1920, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('Red Zone', 2023, 'War', 7.7, 'https://image.tmdb.org/t/p/w500/tB9vjZWEIyDxZOqcGNn3hnr0FQm.jpg', 'War drama', 0, 780, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WhatCarCanYouGetForAGrand.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('Whispers', 2024, 'Horror', 7.4, 'https://image.tmdb.org/t/p/w500/feSiISwgEpVzR1v3zv2n2AU4ANJ.jpg', 'Haunting tale', 0, 620, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
        ('Code Black', 2023, 'Thriller', 8.4, 'https://image.tmdb.org/t/p/w500/yVyNBDyTW0mMmDNTDQ6BRdFKQO5.jpg', 'Cyber thriller', 1, 1650, 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO movies (title, year, genre, rating, image_url, description, is_trending, view_count, video_url, trailer_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_movies)
    
    # Insert sample series
    sample_series = [
        ('Breaking Boundaries', 2023, 'Drama', 9.1, 'https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg', 'Award-winning series', 3),
        ('Cosmic Wars', 2024, 'Sci-Fi', 8.8, 'https://image.tmdb.org/t/p/w500/c8t4w2UYMf5bJHkUSCPSaSBR5X.jpg', 'Epic space saga', 2),
        ('The Detective', 2023, 'Crime', 8.5, 'https://image.tmdb.org/t/p/w500/cNAYI8YD0xOzQlI5ZF6E0KhWWkJ.jpg', 'Crime investigation', 4),
        ('Lost Kingdom', 2024, 'Fantasy', 8.9, 'https://image.tmdb.org/t/p/w500/uKvVjHNqB5VmOrdxqAt2F7J78ED.jpg', 'Fantasy adventure', 2),
        ('Night Shift', 2023, 'Thriller', 8.2, 'https://image.tmdb.org/t/p/w500/3V4kLQg0kSqPLctI5ziYWabAZYF.jpg', 'Medical thriller', 3),
        ('Family Ties', 2024, 'Comedy', 7.9, 'https://image.tmdb.org/t/p/w500/7Cp0ev29fqq9TiJTyxIBzXrh5Fa.jpg', 'Family comedy', 5),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO series (title, year, genre, rating, image_url, description, seasons)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_series)
    
    conn.commit()
    conn.close()

# Initialize database on first run
with app.app_context():
    init_db()

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
