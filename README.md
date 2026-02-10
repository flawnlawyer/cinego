# CINEGO - Movie Streaming Website

A modern, cinematic movie streaming website built with Flask, Jinja2, and SQLite.

## Features

- 🎬 **User Authentication** - Secure login and registration with password hashing
- 🎥 **Movie Catalog** - Browse extensive movie and TV series collections
- ▶️ **Video Streaming** - Click any movie to watch with full-screen player
- ⌨️ **Keyboard Controls** - Space to play/pause, arrows for seek/volume, F for fullscreen
- 🔥 **Trending Section** - Discover what's hot right now
- 📊 **Statistics Dashboard** - View platform statistics
- 🎨 **Modern Dark UI** - Sleek, cinematic design with gradient accents
- 📱 **Responsive Design** - Works on all devices
- ⚡ **Fast & Lightweight** - SQLite database for quick performance

## Technology Stack

- **Backend**: Python Flask
- **Template Engine**: Jinja2
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Icons**: Font Awesome 6
- **Fonts**: Google Fonts (Bebas Neue, Outfit)

## Project Structure

```
cinego/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── instance/
│   └── cinego.db         # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/               # JavaScript files
│   └── images/           # Static images
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Homepage
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── movies.html       # Movies listing
    ├── series.html       # TV series listing
    └── movie_detail.html # Movie details
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
cd cinego
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 3: Access the Website

1. Open your browser and go to `http://localhost:5000`
2. You'll be redirected to the login page
3. Click "Sign up here" to create a new account
4. After registration, login with your credentials
5. Start browsing movies and series!

## Default Features

### Database
- The SQLite database is automatically created on first run
- Sample movies and TV series are pre-loaded
- User passwords are securely hashed using Werkzeug

### Sample Data
The application comes with:
- 15 sample movies across various genres
- 6 sample TV series
- Trending indicators for popular content
- View count tracking

## Usage Guide

### Creating an Account
1. Click "Sign up here" on the login page
2. Enter username, email, and password
3. Confirm your password
4. Click "Sign Up"

### Browsing Content
- **Home**: View all content categories
- **Movies**: Browse all available movies
- **TV Series**: Explore TV series collection
- **Trending**: See what's popular

### Watching Movies
1. **Click any movie card** to open the video player
2. Movie starts playing automatically
3. **Keyboard Controls**:
   - `Space` - Play/Pause
   - `→` - Forward 10 seconds
   - `←` - Backward 10 seconds
   - `↑` - Volume up
   - `↓` - Volume down
   - `F` - Toggle fullscreen
4. See recommended movies after watching
5. Share or add to your list

### Statistics
The homepage displays:
- Number of trending movies
- Total movies available
- Total TV series available

## Customization

### Adding Movies
Edit `app.py` and add entries to the `sample_movies` list in the `init_db()` function:

```python
('Movie Title', 2024, 'Genre', 8.5, 'image_url', 'Description', is_trending, view_count, 'video_url', 'trailer_url')
```

**Video URLs can be:**
- Direct MP4 files: `/static/videos/movie.mp4`
- Cloud storage: `https://your-cdn.com/video.mp4`
- YouTube embeds: `https://youtube.com/embed/VIDEO_ID`

See `VIDEO_STREAMING_GUIDE.md` for detailed instructions on adding your own videos.

### Styling
Modify `static/css/style.css` to customize:
- Colors (CSS variables in `:root`)
- Fonts
- Layout
- Animations

### Database
To reset the database:
1. Stop the application
2. Delete `instance/cinego.db`
3. Restart the application (database will be recreated)

## Security Notes

⚠️ **Important**: Before deploying to production:

1. Change the secret key in `app.py`:
   ```python
   app.secret_key = 'your-secure-random-secret-key'
   ```

2. Disable debug mode:
   ```python
   app.run(debug=False)
   ```

3. Use environment variables for sensitive data
4. Implement HTTPS
5. Add rate limiting for login attempts
6. Use a production WSGI server (Gunicorn, uWSGI)

## Features Roadmap

- [ ] Movie search functionality
- [ ] Genre filtering
- [ ] User watchlist
- [ ] Movie player integration
- [ ] User reviews and ratings
- [ ] Admin panel
- [ ] Email verification
- [ ] Password reset functionality
- [ ] Social media integration

## Troubleshooting

### Database Issues
If you encounter database errors:
```bash
rm instance/cinego.db
python app.py
```

### Module Not Found
Install missing dependencies:
```bash
pip install -r requirements.txt
```

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## License

This project is open source and available for educational purposes.

## Credits

- Design inspired by modern streaming platforms
- Movie data structure based on industry standards
- Icons by Font Awesome
- Fonts by Google Fonts

## Support

For issues or questions, please create an issue in the repository.

---

**Built  using Flask and Jinja2**
