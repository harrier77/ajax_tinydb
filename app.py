from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
JSON_FILE = os.path.join(DATA_DIR, 'database.json')
CONFIG_FILE = os.path.join(PROJECT_DIR, 'config', 'config.json')

CURRENT_DB = 'database.json'

def load_config():
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_json_path():
    return os.path.join(DATA_DIR, CURRENT_DB)

def load_json():
    path = get_json_path()
    
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and data.get('_db_pointer'):
            target = data.get('target') or data.get('path')
            if target:
                if os.path.isabs(target):
                    pointer_path = target
                else:
                    pointer_path = os.path.abspath(os.path.join(PROJECT_DIR, target))
                    if not os.path.exists(pointer_path):
                        pointer_path = os.path.abspath(os.path.join(DATA_DIR, target))
                if os.path.isfile(pointer_path):
                    with open(pointer_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                elif os.path.isdir(pointer_path):
                    root_file = os.path.join(pointer_path, 'root.json')
                    if os.path.exists(root_file):
                        with open(root_file, 'r', encoding='utf-8') as f:
                            root_data = json.load(f)
                        subdir = root_data.get('path')
                        if subdir:
                            pointer_path = os.path.join(pointer_path, subdir)
                    return load_directory(pointer_path)
        
        if isinstance(data, dict) and data.get('path'):
            target_path = data.get('path')
            if os.path.isabs(target_path):
                pointer_path = target_path
            else:
                pointer_path = os.path.abspath(os.path.join(PROJECT_DIR, target_path))
            
            if os.path.isfile(pointer_path):
                with open(pointer_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif os.path.isdir(pointer_path):
                root_file = os.path.join(pointer_path, 'root.json')
                if os.path.exists(root_file):
                    with open(root_file, 'r', encoding='utf-8') as f:
                        root_data = json.load(f)
                    subdir = root_data.get('path')
                    if subdir:
                        pointer_path = os.path.join(pointer_path, subdir)
                return load_directory(pointer_path)
        return data
    
    elif os.path.isdir(path):
        return load_directory(path)
    
    return {}

def load_directory(dir_path):
    dir_name = os.path.basename(dir_path)
    result = {dir_name: {}}
    
    for filename in os.listdir(dir_path):
        if filename.startswith('.'):
            continue
        file_path = os.path.join(dir_path, filename)
        if filename.endswith('.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                doc_id = filename[:-5]
                result[dir_name][doc_id] = data
            except:
                pass
    return result

def get_databases():
    databases = []
    for item in os.listdir(DATA_DIR):
        if item == '.gitignore':
            continue
        item_path = os.path.join(DATA_DIR, item)
        if os.path.isfile(item_path) and item.endswith('.json'):
            databases.append(item)
    return sorted(databases)

def save_json(data):
    path = get_json_path()
    
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
        
        if isinstance(file_data, dict) and file_data.get('_db_pointer'):
            target = file_data.get('target')
            if target:
                pointer_path = os.path.join(DATA_DIR, target)
                if os.path.isdir(pointer_path):
                    root_file = os.path.join(pointer_path, 'root.json')
                    if os.path.exists(root_file):
                        with open(root_file, 'r', encoding='utf-8') as f:
                            root_data = json.load(f)
                        subdir = root_data.get('path')
                        if subdir:
                            pointer_path = os.path.join(pointer_path, subdir)
                    for collection_name, collection_data in data.items():
                        file_path = os.path.join(pointer_path, f"{collection_name}.json")
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(collection_data, f, indent=2, ensure_ascii=False)
                    return
        
        if isinstance(file_data, dict) and file_data.get('path'):
            target_path = file_data.get('path')
            if os.path.isabs(target_path):
                pointer_path = target_path
            else:
                pointer_path = os.path.join(os.path.dirname(path), target_path)
            
            if os.path.isdir(pointer_path):
                root_file = os.path.join(pointer_path, 'root.json')
                if os.path.exists(root_file):
                    with open(root_file, 'r', encoding='utf-8') as f:
                        root_data = json.load(f)
                    subdir = root_data.get('path')
                    if subdir:
                        pointer_path = os.path.join(pointer_path, subdir)
                for collection_name, collection_data in data.items():
                    file_path = os.path.join(pointer_path, f"{collection_name}.json")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(collection_data, f, indent=2, ensure_ascii=False)
                return
    
    elif os.path.isdir(path):
        for collection_name, collection_data in data.items():
            file_path = os.path.join(path, f"{collection_name}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(collection_data, f, indent=2, ensure_ascii=False)
        return
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    data = load_json()
    databases = get_databases()
    config = load_config()
    return render_template('client_app.html', data=data, databases=databases, current_db=CURRENT_DB, config=config)

@app.route('/select-db', methods=['POST'])
def select_db():
    global CURRENT_DB
    database = request.form.get('database')
    if database:
        CURRENT_DB = database
    databases = get_databases()
    config = load_config()
    return render_template('client_app.html', data=load_json(), databases=databases, current_db=CURRENT_DB, config=config)

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
        
        parts = field_path.split('|')
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
