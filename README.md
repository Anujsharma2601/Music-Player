🎵 Modern Flask Music Player

A sleek, lightweight web-based music streaming application built with Python (Flask), modern HTML5/CSS3 glassmorphism, and direct audio streaming. Features full-length 320 kbps audio playback, zero required API keys, light/dark mode with custom soundwave artwork, and client-side favorites persistence.

✨ Features
🎧 Full-Length 320 kbps Audio Streaming: Direct high-bitrate audio streaming (.mp4/.m4a) powered by JioSaavn's direct CDN engine with on-the-fly DES decryption. No 30-second preview limitations!
🔍 Hybrid Multi-Tier Search Engine:
Song Title Search: Instant matching for individual tracks (e.g. Kesariya, Perfect, Charkha).
Artist & Greatest Hits Discovery: Automatically surfaces top hits when searching for artist names (e.g. Alfaaz, Arijit Singh, Yo Yo Honey Singh, Ed Sheeran).
iTunes Catalog Backfill: Fallback integration ensuring 100% music coverage with zero missing tracks.
🌓 Light & Dark Mode Switcher:
Custom soundwave & audio equalizer backgrounds (bg-dark.png and bg-light.png).
Smooth theme switcher button anchored in the header.
Persistent theme selection saved in browser localStorage with zero-flash loading.
❤️ Favorites System:
Save your favorite songs with one click (🤍 / ❤️) directly from the track cards or inside the player modal.
Client-side storage powered by localStorage — works instantly with zero database configuration needed.
Dedicated "My Favorites" tab with a live badge counter.
🎨 Modern Glassmorphic UI:
Frosted-glass modals, search bar, and song cards (backdrop-filter: blur).
High-resolution album artwork upscaled to 500x500.
Responsive layout optimized for desktop, tablet, and mobile browsers.
⚡ Zero Configuration: Works out of the box with no API keys, tokens, or logins required.
🛠️ Tech Stack
Backend: Python 3.10+, Flask
Streaming & Cryptography: pyDes
 (DES-ECB audio stream decryption), Requests
Frontend: Semantic HTML5, Modern CSS3 (Variables, Flexbox, Glassmorphism, Animations), Vanilla JavaScript (Web Audio API, LocalStorage)
📁 Project Structure
text
music-player/
├── app.py              # Flask server, search routing & audio decryption logic
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules for venv, cache & temp files
├── README.md           # Project documentation
├── templates/
│   ├── index.html      # Main single-page interface & player modal
│   └── player.html     # Standalone player template (optional)
└── static/
    ├── style.css       # Complete responsive styling & theme variables
    ├── bg-dark.png     # Dark mode soundwave background graphic
    └── bg-light.png    # Light mode soundwave background graphic
🚀 Getting Started
1. Prerequisites

Ensure you have Python 3.8+ installed on your machine:

bash
python --version
2. Clone the Repository
bash
git clone https://github.com/your-username/music-player.git
cd music-player
3. Create & Activate a Virtual Environment
Windows (PowerShell):
powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
macOS / Linux:
bash
python3 -m venv venv
source venv/bin/activate
4. Install Dependencies
bash
pip install -r requirements.txt
5. Launch the Application
bash
python app.py
6. Open in Browser

Open your browser and navigate to:

text
http://localhost:5000

(or http://127.0.0.1:5000)

📖 How to Use
Search Songs or Artists: Enter any song name (e.g. Kesariya, Blinding Lights) or artist (e.g. Alfaaz, Sidhu Moose Wala) in the search bar and press Search.
Play Music: Click on any song card to launch the native audio player modal and begin streaming immediately.
Seek & Volume: Use the native HTML5 player scrubber to jump forward/backward or adjust audio levels.
Save Favorites: Click the heart button on any card or inside the player to bookmark songs in the My Favorites tab.
Toggle Themes: Click the ☀️ Light Mode / 🌙 Dark Mode button in the top right to switch visual styles.
🌐 Deploy to Render

When creating a new Web Service on Render
:

Setting	Value
Environment	Python
Region	Any (e.g. Singapore or Oregon)
Branch	main
Build Command	pip install -r requirements.txt
Start Command	gunicorn app:app (or python app.py)
📦 Dependencies
Package	Version	Purpose
Flask	==3.1.0	Lightweight WSGI web application framework
requests	==2.32.3	HTTP library for querying audio endpoints
pyDes	==2.0.1	DES decryption algorithm for JioSaavn CDN audio streams
gunicorn	==23.0.0	Production WSGI HTTP server for Render deployment
python-dotenv	==1.0.1	Environment configuration support
🤝 Contributing

Contributions, issues, and feature requests are welcome!

Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request
📄 License

This project is open-source and available under the MIT License.
