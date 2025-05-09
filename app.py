import os
import csv
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a real secret key!

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
CSV_PATH = os.path.join(DATA_DIR, 'sleep_data.csv')

def init_csv():
    """Initialize CSV file with headers if it doesn't exist or is empty"""
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        headers = [
            'timestamp', 'name', 'age', 'heart_rate', 'activity_level', 
            'sleep_duration', 'room_temperature', 'caffeine_consumption', 
            'alcohol_consumption', 'screen_time', 'sleep_quality'
        ]
        with open(CSV_PATH, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

def get_best_style():
    """Get the best available matplotlib style"""
    available_styles = plt.style.available
    preferred_styles = ['ggplot', 'seaborn', 'bmh', 'fivethirtyeight', 'default']
    for style in preferred_styles:
        if style in available_styles:
            return style
    return 'default'

def predict_sleep_quality(data):
    """Predict sleep quality (1-10) based on input factors"""
    quality = 5.0  # Base score
    
    # Adjust based on factors
    quality += (data['sleep_duration'] - 7) * 0.7
    quality -= (data['heart_rate'] - 65) * 0.08
    quality -= data['screen_time'] * 0.4
    quality -= data['caffeine_consumption'] * 0.3
    quality += data['activity_level'] / 2500
    quality -= (data['room_temperature'] - 20) * 0.1
    quality -= data['alcohol_consumption'] * 0.5
    
    return max(1, min(10, round(quality, 1)))

def create_plot(data):
    """Create visualization of sleep data"""
    try:
        plt.style.use(get_best_style())
        fig = plt.figure(figsize=(12, 16), facecolor='#f5f7fa')
        
        # Convert timestamp to datetime
        data['date'] = pd.to_datetime(data['timestamp'])
        data = data.sort_values('date')
        
        # 1. Sleep Quality Trend
        ax1 = plt.subplot(3, 1, 1)
        line, = ax1.plot(data['date'], data['sleep_quality'], 'o-', color='#3498db', 
                        linewidth=2.5, markersize=8, label='Daily Quality')
        
        # Add trend line
        z = np.polyfit(data['date'].astype(np.int64) // 10**9, data['sleep_quality'], 1)
        p = np.poly1d(z)
        trend_line, = ax1.plot(data['date'], p(data['date'].astype(np.int64) // 10**9), 
                             '--', color='#e74c3c', alpha=0.7, label='Trend')
        
        ax1.set_title('Sleep Quality Trend', pad=20, fontsize=14, fontweight='bold')
        ax1.set_ylabel('Sleep Score (1-10)', labelpad=10)
        ax1.set_ylim(0, 10.5)
        ax1.grid(True, linestyle='--', alpha=0.4)
        ax1.legend(handles=[line, trend_line])
        
        # 2. Factors Radar Chart
        ax2 = plt.subplot(3, 1, 2, polar=True)
        factors = ['sleep_duration', 'heart_rate', 'screen_time', 'caffeine_consumption', 'activity_level']
        labels = ['Sleep Hours', 'Heart Rate', 'Screen Time', 'Caffeine', 'Activity']
        
        # Normalize data
        normalized = data[factors].iloc[-1].values
        normalized[0] = normalized[0]/10
        normalized[1] = 1 - (normalized[1]-50)/100
        normalized[2] = 1 - normalized[2]/8
        normalized[3] = 1 - normalized[3]/5
        normalized[4] = normalized[4]/10000
        
        angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        normalized = np.concatenate((normalized, [normalized[0]]))
        
        ax2.plot(angles, normalized, 'o-', linewidth=2, color='#3498db')
        ax2.fill(angles, normalized, alpha=0.25, color='#3498db')
        ax2.set_thetagrids(angles[:-1] * 180/np.pi, labels)
        ax2.set_title('Current Night Factors', pad=20, fontsize=14, fontweight='bold')
        ax2.grid(True)
        
        # 3. Sleep Quality Distribution
        ax3 = plt.subplot(3, 1, 3)
        bins = np.arange(1, 11.5, 1)
        ax3.hist(data['sleep_quality'], bins=bins, edgecolor='white', color='#3498db', alpha=0.7)
        
        current_quality = data['sleep_quality'].iloc[-1]
        ax3.axvline(x=current_quality, color='#e74c3c', linestyle='--', linewidth=2)
        
        ax3.set_title('Your Sleep Quality Distribution', pad=20, fontsize=14, fontweight='bold')
        ax3.set_xlabel('Sleep Quality Score', labelpad=10)
        ax3.set_ylabel('Frequency', labelpad=10)
        ax3.grid(True, axis='y', linestyle='--', alpha=0.4)
        
        plt.tight_layout(pad=3.0)
        
        # Save plot to bytes
        img = BytesIO()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight', facecolor=fig.get_facecolor())
        img.seek(0)
        plt.close()
        
        return base64.b64encode(img.getvalue()).decode('utf8')
    
    except Exception as e:
        plt.close()
        raise RuntimeError(f"Error generating plot: {str(e)}")

def generate_suggestions(data):
    """Generate personalized sleep improvement suggestions"""
    latest = data.iloc[-1]
    suggestions = []
    
    # Sleep duration
    if latest['sleep_duration'] < 6:
        suggestions.append(("⏰ Sleep Duration", 
                          f"Only {latest['sleep_duration']} hours (recommended: 7-9 hours)",
                          "Try going to bed 30 minutes earlier"))
    elif latest['sleep_duration'] > 9:
        suggestions.append(("⏰ Sleep Duration", 
                          f"{latest['sleep_duration']} hours (may cause grogginess)",
                          "Set a consistent wake-up time"))
    
    # Heart rate
    if latest['heart_rate'] > 80:
        suggestions.append(("❤️ Heart Rate", 
                          f"High resting rate: {latest['heart_rate']} bpm",
                          "Practice relaxation techniques"))
    
    # Screen time
    if latest['screen_time'] > 2:
        suggestions.append(("📱 Screen Time", 
                          f"{latest['screen_time']} hours before bed",
                          "Establish screen-free time before sleep"))
    
    # Caffeine
    if latest['caffeine_consumption'] > 2:
        suggestions.append(("☕ Caffeine", 
                          f"{latest['caffeine_consumption']} cups consumed",
                          "Limit caffeine after 2pm"))
    
    # Alcohol
    if latest['alcohol_consumption'] > 1:
        suggestions.append(("🍷 Alcohol", 
                          f"{latest['alcohol_consumption']} drinks consumed",
                          "Reduce alcohol intake, especially in the evening, to improve sleep quality"))

    # Activity
    if latest['activity_level'] < 5000:
        suggestions.append(("🚶 Activity", 
                          f"Only {latest['activity_level']} steps",
                          "Aim for 7,000+ steps daily"))
    
    # Temperature
    if latest['room_temperature'] > 22:
        suggestions.append(("🌡️ Temperature", 
                          f"Room: {latest['room_temperature']}°C (ideal: 18-21°C)",
                          "Cool your bedroom before sleep"))
    
    if not suggestions and latest['sleep_quality'] >= 7:
        suggestions.append(("🌟 Great Job!", 
                          "Your sleep habits are excellent!",
                          "Keep up the good work!"))
    
    return suggestions

@app.route('/', methods=['GET', 'POST'])
def index():
    init_csv()  # Ensure CSV exists
    
    if request.method == 'POST':
        try:
            # Get form data
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            input_data = {
                'name': request.form['name'],
                'age': int(request.form['age']),
                'heart_rate': int(request.form['heart_rate']),
                'activity_level': int(request.form['activity_level']),
                'sleep_duration': float(request.form['sleep_duration']),
                'room_temperature': float(request.form['room_temp']),
                'caffeine_consumption': int(request.form['caffeine']),
                'alcohol_consumption': int(request.form['alcohol']),
                'screen_time': float(request.form['screen_time'])
            }
            
            # Predict sleep quality
            sleep_quality = predict_sleep_quality(input_data)
            
            # Save to CSV
            with open(CSV_PATH, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    input_data['name'],
                    input_data['age'],
                    input_data['heart_rate'],
                    input_data['activity_level'],
                    input_data['sleep_duration'],
                    input_data['room_temperature'],
                    input_data['caffeine_consumption'],
                    input_data['alcohol_consumption'],
                    input_data['screen_time'],
                    sleep_quality
                ])
            
            flash(f"Data saved! Your sleep quality: {sleep_quality}/10", 'success')
            return redirect(url_for('index'))

        except ValueError as e:
            flash(f"Invalid input: {str(e)}", 'error')
    
    # Load existing data
    try:
        df = pd.read_csv(CSV_PATH)
        if len(df) > 1:
            plot_url = create_plot(df)
            suggestions = generate_suggestions(df)
        else:
            plot_url = None
            suggestions = None
    except Exception as e:
        flash(f"Error loading data: {str(e)}", 'error')
        df = None
        plot_url = None
        suggestions = None
    
    return render_template('index.html', plot_url=plot_url, suggestions=suggestions)

# Initialize on startup
with app.app_context():
    init_csv()

if __name__ == '__main__':
    app.run(debug=True)
