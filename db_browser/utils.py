# -*- coding: utf-8 -*-
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
    print("ATTENZIONE: File config con le label assente. Posizionarlo in db_brow/config/config.json")
    return {"labelFields": []}

def get_json_path():
    return os.path.join(DATA_DIR, CURRENT_DB)

def load_json():
    path = get_json_path()

    
    if os.path.isfile(path):
        print(f"[DEBUG load_json] E' un file")
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        
        target = data.get('target') if isinstance(data, dict) else None

        if target:
            print(f"[DEBUG load_json] Risoluzione target: {target}")
            
            if os.path.isabs(target):
                pointer_path = target
            else:
                pointer_dir = os.path.dirname(path)
                pointer_path = os.path.abspath(os.path.join(pointer_dir, target))
                print(f"[DEBUG load_json]Rispetto a pointer dir {pointer_dir}: {pointer_path}")
            

            
            if os.path.isfile(pointer_path):
                print(f"[DEBUG load_json] Carico file JSON: {pointer_path}")
                with open(pointer_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            elif os.path.isdir(pointer_path):
                print(f"[DEBUG load_json] E' una directory, chiamo load_directory")
                return load_directory(pointer_path)
            else:
                print(f"[ERRORE] Percorso non esiste: {pointer_path}")
                return {}
        
        if isinstance(data, list):
            collection_name = os.path.splitext(CURRENT_DB)[0]
            return {collection_name: {str(i): item for i, item in enumerate(data)}}
        
        return data
    
    elif os.path.isdir(path):
        print(f"[DEBUG load_json] E' una directory, chiamo load_directory")
        return load_directory(path)
    
    print(f"[ERRORE] Percorso non esiste: {path}")
    return {}

def load_directory(dir_path):
    if not os.path.isdir(dir_path):
        print(f"[ERRORE] Directory non esiste: {dir_path}")
        return {}
    dir_name = os.path.basename(dir_path)
    result = {dir_name: {}}
    
    files_found = []
    try:
        entries = os.listdir(dir_path)
        print(f"[DEBUG load_directory] Totale entries: {len(entries)}")
        for filename in entries:
            if filename.startswith('.'):
                continue
            file_path = os.path.join(dir_path, filename)
            if filename.endswith('.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    doc_id = filename[:-5]
                    if isinstance(data, list):
                        result[dir_name][doc_id] = data
                    else:
                        result[dir_name][doc_id] = data
                    
                    files_found.append(filename)
                except json.JSONDecodeError as e:
                    print(f"[ERRORE] JSON non valido {filename}: {e}")
                except Exception as e:
                    print(f"[ERRORE] Lettura {filename}: {e}")
            else:
                print(f"[DEBUG load_directory] Skip non-JSON: {filename}")
    except PermissionError as e:
        print(f"[ERRORE] Permesso negato: {dir_path}: {e}")
    except Exception as e:
        print(f"[ERRORE] Lettura directory {dir_path}: {e}")
    
    print(f"\n[DEBUG load_directory] FINE")
    print(f"[DEBUG load_directory] File caricati: {len(files_found)}")
    print(f"[DEBUG load_directory] result keys: {list(result.keys())}")
    print(f"{'='*60}\n")
    
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

def save_json(data, doc_id=None, collection=None):
    path = get_json_path()

    print(f"{'='*60}")
    
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
        
        target = file_data.get('target') if isinstance(file_data, dict) else None
        print(f"[DEBUG save_json] target nel file pointer: {target}")
        
        if target:
            if os.path.isabs(target):
                pointer_path = target
            else:
                pointer_dir = os.path.dirname(path)
                pointer_path = os.path.abspath(os.path.join(pointer_dir, target))
            
            print(f"[DEBUG save_json] pointer_path: {pointer_path}")
            
            if os.path.isdir(pointer_path):
                # CASO: Pointer a directory
                # Se abbiamo doc_id e collection, salviamo solo quel file
                if doc_id and collection and collection in data:
                    doc_data = data[collection].get(str(doc_id))
                    if doc_data is not None:
                        file_path = os.path.join(pointer_path, f"{doc_id}.json")
                        print(f"[DEBUG save_json] Salvo solo file specifico: {file_path}")
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(doc_data, f, indent=2, ensure_ascii=False)
                        print(f"[DEBUG save_json] Salvataggio completato")
                        return
                    else:
                        print(f"[DEBUG save_json] doc_id non trovato, fallback a salvataggio completo")
                
                # DEFAULT: Salva tutti i file (retrocompatibile)
                for collection_name, collection_data in data.items():
                    if isinstance(collection_data, dict):
                        for doc_id_key, doc_data in collection_data.items():
                            file_path = os.path.join(pointer_path, f"{doc_id_key}.json")
                            print(f"[DEBUG save_json] Scrivo: {file_path}")
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(doc_data, f, indent=2, ensure_ascii=False)
                print(f"[DEBUG save_json] Salvataggio completato")
                return
    
    elif os.path.isdir(path):
        # CASO: Directory (non pointer)
        for collection_name, collection_data in data.items():
            if isinstance(collection_data, dict):
                for doc_id_key, doc_data in collection_data.items():
                    file_path = os.path.join(path, f"{doc_id_key}.json")
                    print(f"[DEBUG save_json] Scrivo: {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(doc_data, f, indent=2, ensure_ascii=False)
        print(f"[DEBUG save_json] Salvataggio completato")
        return
    
    # CASO: File unico (retrocompatibile)
    print(f"[DEBUG save_json] Scrivo file diretto: {path}")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[DEBUG save_json] FINE")
