from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import subprocess
import os
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def upload_page():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'user_uploaded.xlsx')
    file.save(upload_path)

    # Run sentiment enrichment (Node.js)
    subprocess.run(['node', 'process_sentiment.js'])

    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    processed_path = os.path.join(PROCESSED_FOLDER, 'sbi_enriched_sentiment_data.xlsx')
    has_data = os.path.exists(processed_path)
    
    if not has_data:
        return render_template('dashboard.html',
                               sentiment_dist={},
                               platform_sentiment=[],
                               topic_sentiment=[],
                               no_data=True,
                               has_data=False)
    
    df = pd.read_excel(processed_path)
    if df.empty or 'sentiment' not in df or 'platform' not in df or 'text' not in df:
        return render_template('dashboard.html',
                               sentiment_dist={},
                               platform_sentiment=[],
                               topic_sentiment=[],
                               no_data=True,
                               has_data=False)
    def get_topic(text):
        if pd.isna(text):
            return 'Other'
        text = str(text).lower()
        if 'claim' in text:
            return 'Claims'
        elif 'service' in text:
            return 'Service'
        elif 'price' in text:
            return 'Pricing'
        else:
            return 'Other'
    df['topic'] = df['text'].apply(get_topic)
    total_mentions = len(df)
    sentiment_dist = df['sentiment'].value_counts().to_dict()
    platform_sentiment = (
        df.groupby(['platform', 'sentiment']).size().unstack(fill_value=0)
        .reset_index()
        .to_dict(orient='records')
    )
    topic_sentiment = (
        df.groupby(['topic', 'sentiment']).size().unstack(fill_value=0)
        .reset_index()
        .to_dict(orient='records')
    )
    return render_template('dashboard.html',
                           sentiment_dist=sentiment_dist,
                           platform_sentiment=platform_sentiment,
                           topic_sentiment=topic_sentiment,
                           total_mentions=total_mentions,
                           no_data=False,
                           has_data=True)

@app.route('/download')
def download_file():
    processed_path = os.path.join(PROCESSED_FOLDER, 'sbi_enriched_sentiment_data.xlsx')
    if os.path.exists(processed_path):
        return send_file(processed_path, as_attachment=True, download_name='sbi_enriched_sentiment_data.xlsx')
    else:
        return 'File not found', 404

if __name__ == '__main__':
    app.run(debug=True)
