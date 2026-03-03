from flask import Blueprint, render_template, request, jsonify
from .utils import (
    load_json,
    load_config,
    get_databases,
    save_json,
    get_current_db,
    set_current_db
)

bp = Blueprint('db_browser', __name__, template_folder='templates')

@bp.route('/')
def index():
    data = load_json()
    databases = get_databases()
    config = load_config()
    return render_template('client_app.html', data=data, databases=databases, current_db=get_current_db(), config=config)

@bp.route('/select-db', methods=['POST'])
def select_db():
    database = request.form.get('database')
    if database:
        set_current_db(database)
    databases = get_databases()
    config = load_config()
    return render_template('client_app.html', data=load_json(), databases=databases, current_db=get_current_db(), config=config)

@bp.route('/api/save', methods=['POST'])
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
        
        save_json(data, doc_id=doc_id, collection=collection)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.run(debug=True, host='0.0.0.0', port=5000)
