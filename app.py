from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
JSON_FILE = os.path.join(DATA_DIR, 'database.json')

def load_json():
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    data = load_json()
    return render_template('client_app.html', data=data)

@app.route('/api/save', methods=['POST'])
def save_field():
    try:
        payload = request.json
        collection = payload.get('collection')
        doc_id = payload.get('doc_id')
        field_path = payload.get('field_path')
        new_value = payload.get('value')
        
        data = load_json()
        
        if collection not in data:
            return jsonify({'success': False, 'error': 'Collection not found'}), 404
        
        doc = data[collection].get(str(doc_id))
        if not doc:
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        parts = field_path.split('.')
        current = doc
        for part in parts[:-1]:
            if part.isdigit():
                part = int(part)
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    current = current[int(part)]
                except:
                    return jsonify({'success': False, 'error': 'Invalid path'}), 400
        
        final_key = parts[-1]
        if final_key.isdigit():
            final_key = int(final_key)
        
        if isinstance(current, dict):
            current[final_key] = new_value
        elif isinstance(current, list):
            current[int(final_key)] = new_value
        
        save_json(data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
