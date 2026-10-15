import os
import json
from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit to 16 MB

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith('.log') or filename.endswith('.txt'):
            lines = file.read().decode('utf-8', errors='ignore').splitlines()
            df = pd.DataFrame({'log_entry': lines})
        else:
            return jsonify({'error': 'Unsupported file type (.csv, .log, .txt only)'}), 400

        total_rows = len(df)
        total_cols = len(df.columns)
        columns = list(df.columns)
        
        preview = df.head(10).fillna('').to_dict(orient='records')

        error_count = 0
        if 'log_entry' in df.columns:
            error_count = int(df['log_entry'].str.contains('ERROR|CRITICAL|FAIL', case=False, regex=True).sum())

        return jsonify({
            'success': True,
            'filename': file.filename,
            'total_rows': total_rows,
            'total_cols': total_cols,
            'columns': columns,
            'error_count': error_count,
            'preview': preview
        })

    except Exception as e:
        return jsonify({'error': f'Parsing error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
            
