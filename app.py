import os
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
CSV_PATH = os.path.join(DATA_DIR, 'sleep_data.csv')

def init_csv():
    """Initialize CSV file with headers if it doesn't exist"""
    if not os.path.exists(CSV_PATH):
        headers = [
            'timestamp', 'name', 'age', 'heart_rate', 'activity_level', 
            'sleep_duration', 'room_temperature', 'caffeine_consumption', 
            'alcohol_consumption', 'screen_time', 'sleep_quality'
        ]
        with open(CSV_PATH, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

def predict_sleep_quality(data):
    """Predict sleep quality (1-10) based on input factors"""
    quality = 5.0  # Base score
    
    # Adjust based on factors (simple linear model)
    quality += (data['sleep_duration'] - 7) * 0.5
    quality -= (data['heart_rate'] - 70) * 0.05
    quality -= data['screen_time'] * 0.3
    quality -= data['caffeine_consumption'] * 0.2
    quality += data['activity_level'] / 2000
    
    # Ensure score stays between 1-10
    return max(1, min(10, round(quality, 1)))

def create_plot(data):
    """Create visualization of sleep data"""
    plt.figure(figsize=(10, 8))
    
    # Convert timestamp to datetime
    data['date'] = pd.to_datetime(data['timestamp'])
    
    # 1. Sleep Quality Over Time
    plt.subplot(2, 1, 1)
    plt.plot(data['date'], data['sleep_quality'], 'bo-')
    plt.title('Your Sleep Quality Over Time')
    plt.xlabel('Date')
    plt.ylabel('Sleep Score (1-10)')
    plt.ylim(0, 10.5)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 2. Factors Affecting Sleep
    plt.subplot(2, 1, 2)
    factors = {
        'Sleep Hours': data['sleep_duration'].mean(),
        'Heart Rate': data['heart_rate'].mean(),
        'Screen Time': data['screen_time'].mean(),
        'Activity': data['activity_level'].mean()/1000
    }
    
    colors = ['#4CAF50', '#F44336', '#2196F3', '#FFC107']
    plt.bar(factors.keys(), factors.values(), color=colors)
    plt.title('Average Daily Factors')
    plt.ylabel('Amount')
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.axhline(y=7, color='#4CAF50', linestyle='--', label='Ideal Sleep')
    plt.axhline(y=70, color='#F44336', linestyle='--', label='Ideal HR')
    plt.legend()
    
    plt.tight_layout()
    
    # Save plot to bytes
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode('utf8')

@app.route('/', methods=['GET', 'POST'])
def index():
    init_csv()
    
    if request.method == 'POST':
        try:
            # Get form data
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            name = request.form['name']
            age = int(request.form['age'])
            heart_rate = int(request.form['heart_rate'])
            activity_level = int(request.form['activity_level'])
            sleep_duration = float(request.form['sleep_duration'])
            room_temp = float(request.form['room_temp'])
            caffeine = int(request.form['caffeine'])
            alcohol = int(request.form['alcohol'])
            screen_time = float(request.form['screen_time'])

            # Predict sleep quality
            input_data = {
                'sleep_duration': sleep_duration,
                'heart_rate': heart_rate,
                'screen_time': screen_time,
                'caffeine_consumption': caffeine,
                'activity_level': activity_level
            }
            sleep_quality = predict_sleep_quality(input_data)

            # Save to CSV
            with open(CSV_PATH, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, name, age, heart_rate, activity_level, sleep_duration,
                    room_temp, caffeine, alcohol, screen_time, sleep_quality
                ])
            
            flash(f"Data saved successfully! Your sleep quality: {sleep_quality}/10", 'success')
            return redirect(url_for('index'))

        except ValueError as e:
            flash(f"Invalid input: {str(e)}", 'error')
    
    # Load existing data
    try:
        df = pd.read_csv(CSV_PATH)
        plot_url = create_plot(df) if len(df) > 1 else None
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = None
        plot_url = None
    
    return render_template('index.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)