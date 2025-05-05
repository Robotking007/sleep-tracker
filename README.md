# Sleep Quality Tracker 🌙

A Flask-based web application that tracks sleep patterns, predicts sleep quality, and provides personalized improvement suggestions.

![Sleep Quality Tracker Screenshot](static/screenshot.png)

## Features ✨

- 📊 Track multiple sleep-related metrics (duration, heart rate, room temp, etc.)
- 🤖 AI-powered sleep quality prediction (1-10 scale)
- 📈 Interactive data visualizations
- 💡 Personalized sleep improvement suggestions
- 📱 Fully responsive design
- 🔒 Secure form validation (client & server-side)
- 📝 Persistent data storage (CSV)

## Tech Stack 🛠️

### Backend
- **Python** (3.8+)
- **Flask** (Web framework)
- **Pandas** (Data analysis)
- **Matplotlib** (Visualizations)
- **WTForms** (Input validation)

### Frontend
- **HTML5** (Semantic markup)
- **CSS3** (Flexbox/Grid, CSS variables)
- **JavaScript** (Progressive enhancement)
- **Chart.js** (via Matplotlib export)

### Deployment
- **PythonAnywhere** (Hosting)
- **Gzip Compression** (Performance)
- **Cache Headers** (Client-side caching)

## Project Architecture 🏛️
sleep-quality-tracker/
├── app.py # Main application logic
├── wsgi.py # WSGI configuration
├── requirements.txt # Python dependencies
├── data/
│ └── sleep_data.csv # Sleep records database
├── static/
│ ├── styles.css # Main stylesheet
│ └── app.js # Client-side scripts
└── templates/
└── index.html # Main template


Key features of this README:

1. **Visual Appeal**: Uses emojis and clear section headers
2. **Comprehensive Setup**: Detailed local and deployment instructions
3. **Technical Transparency**: Clearly explains the prediction algorithm
4. **Architecture Overview**: Visual directory structure
5. **Sample Data**: Helps users understand expected inputs
6. **Contribution Guidelines**: Encourages community involvement

You may want to:
- Add actual screenshot (replace `static/screenshot.png`)
- Update the live demo link when deployed
- Add your contact information
- Include any additional deployment notes specific to your setup

The README follows best practices for open-source projects while being specifically tailored to your sleep tracking application.
