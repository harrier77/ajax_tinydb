import json
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
CONFIG_FILE = os.path.join(PROJECT_DIR, 'config', 'config.json')

CURRENT_DB = 'database.json'

def set_current_db(db_name):
    global CURRENT_DB
    CURRENT_DB = db_name

def get_current_db():
    return CURRENT_DB

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
        
        if isinstance(data, list):
            collection_name = os.path.splitext(CURRENT_DB)[0]
            return {collection_name: {str(i): item for i, item in enumerate(data)}}
        
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
                if isinstance(data, list):
                    for idx, item in enumerate(data):
                        result[dir_name][f"{doc_id}_{idx}"] = item
                else:
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
