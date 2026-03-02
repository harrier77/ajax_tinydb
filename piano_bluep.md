# Piano di Trasformazione: db_browser.py → Blueprint

## Obiettivo
Trasformare `db_browser.py` in un Flask Blueprint mantenendo la possibilità di esecuzione standalone.

## Analisi del Codice Attuale

### Componenti Identificati
1. **Configurazione** (linee 7-13)
   - `PROJECT_DIR`, `DATA_DIR`, `JSON_FILE`, `CONFIG_FILE`
   - `CURRENT_DB` (variabile globale)

2. **Funzioni Utility** (linee 14-113)
   - `load_config()`, `get_json_path()`, `load_json()`
   - `load_directory()`, `get_databases()`, `save_json()`

3. **Route Flask** (linee 171-231)
   - `@app.route('/')` → `index()`
   - `@app.route('/select-db', methods=['POST'])` → `select_db()`
   - `@app.route('/api/save', methods=['POST'])` → `save_field()`

4. **Entry Point** (linee 233-234)
   - Esecuzione standalone con `app.run()`

---

## Piano di Implementazione

### Step 1: Creare la struttura Blueprint
```
db_browser/
├── __init__.py        # Esporta il blueprint
├── routes.py          # Definizione delle route
├── utils.py           # Funzioni utility (load_json, save_json, etc.)
└── standalone.py      # App standalone per testing
```

### Step 2: Modifiche ai File

#### `utils.py`
- Spostare tutte le funzioni di utilità
- Ricevere `DATA_DIR` e `CONFIG_FILE` come parametri o usare blueprint `app_ctx`

#### `routes.py`
- Creare il blueprint: `bp = Blueprint('db_browser', __name__)`
- Definire le route usando `bp.route()` invece di `app.route()`
- Le funzioni utility vengono importate da `utils.py`

#### `__init__.py`
```python
from .routes import bp
__all__ = ['bp']
```

#### `standalone.py` (opzionale, o mantenere in db_browser.py)
```python
from flask import Flask
from db_browser import bp

app = Flask(__name__)
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(...)
```

### Step 3: Mantenere Compatibilità Standalone

**Opzione A**: Mantenere `db_browser.py` come entry point che importa e registra il blueprint

```python
# db_browser.py - versione standalone
from flask import Flask
from db_browser import bp

app = Flask(__name__)
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**Opzione B**: Aggiungere flag condizionale nel modulo routes

```python
# routes.py
bp = Blueprint('db_browser', __name__)

# ... route definitions ...

if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.run(...)
```

---

## Dipendenze da Gestire

1. **Template**: `client_app.html` - deve rimanere accessibile
2. **Configurazione**: `config/config.json`
3. **Data**: `data/database.json`

Il Blueprint dovrà gestire questi path relativi alla directory del blueprint o dell'app registrante.

---

## Ordine di Implementazione Suggerito

1. Creare directory `db_browser/`
2. Creare `utils.py` con le funzioni di utilità
3. Creare `routes.py` con il blueprint
4. Creare `__init__.py`
5. Testare standalone
6. Verificare registrazione in app esterna
