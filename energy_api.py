"""
Energy Dashboard - Local API Server
Reads natural_gas_energy.db and serves data to the dashboard via HTTP.

Usage:
    python energy_api.py

Then open energy-dashboard.html in your browser.
API runs at http://localhost:5000
"""

import sqlite3
import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow the dashboard HTML to call this API

# ── CONFIG ────────────────────────────────────────────────────────────────────
# Put your .db file in the same folder as this script, or set full path here
DB_PATH = os.path.join(os.path.dirname(__file__), 'natural_gas_energy.db')
# ─────────────────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # returns dict-like rows
    return conn


def query(sql, params=()):
    conn = get_db()
    try:
        cur = conn.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        return rows
    finally:
        conn.close()


# ── HEALTH CHECK ──────────────────────────────────────────────────────────────
@app.route('/health')
def health():
    exists = os.path.exists(DB_PATH)
    tables = []
    if exists:
        rows = query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r['name'] for r in rows]
    return jsonify({
        'status': 'ok' if exists else 'error',
        'db_path': DB_PATH,
        'db_found': exists,
        'tables': tables
    })


# ── CATALOG ───────────────────────────────────────────────────────────────────
@app.route('/catalog')
def catalog():
    rows = query("SELECT * FROM _catalog ORDER BY category, table_name")
    return jsonify(rows)


# ── GENERIC TABLE ENDPOINT ────────────────────────────────────────────────────
# GET /table/<name>?limit=100&order=date&dir=desc
@app.route('/table/<table_name>')
def get_table(table_name):
    # Whitelist — only allow real table names to prevent SQL injection
    allowed = query("SELECT name FROM sqlite_master WHERE type='table'")
    allowed_names = [r['name'] for r in allowed]
    if table_name not in allowed_names:
        return jsonify({'error': f'Table {table_name} not found'}), 404

    limit = request.args.get('limit', 500, type=int)
    order = request.args.get('order', None)
    direction = request.args.get('dir', 'desc').upper()
    if direction not in ('ASC', 'DESC'):
        direction = 'DESC'

    sql = f'SELECT * FROM "{table_name}"'
    if order:
        sql += f' ORDER BY "{order}" {direction}'
    sql += f' LIMIT {limit}'

    rows = query(sql)
    return jsonify({'table': table_name, 'count': len(rows), 'data': rows})


# ── SUPPLY & DISPOSITION ──────────────────────────────────────────────────────
@app.route('/natural-gas/supply/monthly')
def supply_monthly():
    limit = request.args.get('limit', 60, type=int)
    rows = query(f'SELECT * FROM supply_monthly ORDER BY date DESC LIMIT {limit}')
    return jsonify({'table': 'supply_monthly', 'count': len(rows), 'data': rows})

@app.route('/natural-gas/supply/annual')
def supply_annual():
    rows = query('SELECT * FROM supply_annual ORDER BY date DESC')
    return jsonify({'table': 'supply_annual', 'count': len(rows), 'data': rows})


# ── IMPORTS & EXPORTS ─────────────────────────────────────────────────────────
@app.route('/natural-gas/imports/monthly')
def imports_monthly():
    limit = request.args.get('limit', 60, type=int)
    rows = query(f'SELECT * FROM imports_monthly ORDER BY date DESC LIMIT {limit}')
    return jsonify({'table': 'imports_monthly', 'count': len(rows), 'data': rows})

@app.route('/natural-gas/imports/annual')
def imports_annual():
    rows = query('SELECT * FROM imports_annual ORDER BY date DESC')
    return jsonify({'table': 'imports_annual', 'count': len(rows), 'data': rows})

@app.route('/natural-gas/exports/monthly')
def exports_monthly():
    limit = request.args.get('limit', 60, type=int)
    rows = query(f'SELECT * FROM exports_monthly ORDER BY date DESC LIMIT {limit}')
    return jsonify({'table': 'exports_monthly', 'count': len(rows), 'data': rows})

@app.route('/natural-gas/exports/annual')
def exports_annual():
    rows = query('SELECT * FROM exports_annual ORDER BY date DESC')
    return jsonify({'table': 'exports_annual', 'count': len(rows), 'data': rows})


# ── WITHDRAWALS ───────────────────────────────────────────────────────────────
@app.route('/natural-gas/withdrawals/monthly')
def withdrawals_monthly():
    limit = request.args.get('limit', 60, type=int)
    rows = query(f'SELECT * FROM withdrawals_areas_monthly ORDER BY date DESC LIMIT {limit}')
    return jsonify({'table': 'withdrawals_areas_monthly', 'count': len(rows), 'data': rows})

@app.route('/natural-gas/withdrawals/annual')
def withdrawals_annual():
    rows = query('SELECT * FROM withdrawals_areas_annual ORDER BY date DESC')
    return jsonify({'table': 'withdrawals_areas_annual', 'count': len(rows), 'data': rows})


# ── PRODUCTION ────────────────────────────────────────────────────────────────
@app.route('/natural-gas/production/monthly')
def production_monthly():
    limit = request.args.get('limit', 60, type=int)
    rows = query(f'SELECT * FROM production_areas_monthly ORDER BY date DESC LIMIT {limit}')
    return jsonify({'table': 'production_areas_monthly', 'count': len(rows), 'data': rows})

@app.route('/natural-gas/production/annual')
def production_annual():
    rows = query('SELECT * FROM production_areas_annual ORDER BY date DESC')
    return jsonify({'table': 'production_areas_annual', 'count': len(rows), 'data': rows})


# ── STORAGE ───────────────────────────────────────────────────────────────────
@app.route('/natural-gas/storage')
def storage():
    limit = request.args.get('limit', 60, type=int)
    rows = query(f'SELECT * FROM storage_all_operators ORDER BY date DESC LIMIT {limit}')
    return jsonify({'table': 'storage_all_operators', 'count': len(rows), 'data': rows})

@app.route('/natural-gas/storage/seasonal')
def storage_seasonal():
    rows = query('SELECT * FROM storage_by_season ORDER BY date DESC')
    return jsonify({'table': 'storage_by_season', 'count': len(rows), 'data': rows})


# ── SUMMARY (for dashboard overview cards) ────────────────────────────────────
@app.route('/summary')
def summary():
    """Returns latest single values for key metrics — used by dashboard cards."""
    results = {}

    def latest(table, col):
        try:
            rows = query(f'SELECT "{col}" FROM "{table}" WHERE "{col}" IS NOT NULL ORDER BY date DESC LIMIT 1')
            return rows[0][col] if rows else None
        except:
            return None

    def latest2(table, col):
        try:
            rows = query(f'SELECT "{col}" FROM "{table}" WHERE "{col}" IS NOT NULL ORDER BY date DESC LIMIT 2')
            return [r[col] for r in rows] if rows else []
        except:
            return []

    # Supply
    sup = latest2('supply_monthly', 'dry_natural_gas_production_bcf')
    results['dry_gas_production_bcf'] = {'current': sup[0] if sup else None, 'prev': sup[1] if len(sup)>1 else None}

    sup2 = latest2('supply_monthly', 'total_consumption_bcf')
    results['total_consumption_bcf'] = {'current': sup2[0] if sup2 else None, 'prev': sup2[1] if len(sup2)>1 else None}

    # Storage
    stor = latest2('storage_all_operators', 'total_underground_storage_bcf') or latest2('storage_all_operators', list(query('PRAGMA table_info(storage_all_operators)')[1]['name'] if query('PRAGMA table_info(storage_all_operators)') else [{}])[0] if False else None)
    try:
        cols = [r['name'] for r in query('PRAGMA table_info(storage_all_operators)') if r['name'] != 'date']
        if cols:
            stor = latest2('storage_all_operators', cols[0])
            results['storage'] = {'current': stor[0] if stor else None, 'prev': stor[1] if len(stor)>1 else None, 'column': cols[0]}
    except:
        pass

    # Imports / Exports
    try:
        imp_cols = [r['name'] for r in query('PRAGMA table_info(imports_monthly)') if r['name'] != 'date']
        if imp_cols:
            imp = latest2('imports_monthly', imp_cols[0])
            results['imports'] = {'current': imp[0] if imp else None, 'prev': imp[1] if len(imp)>1 else None, 'column': imp_cols[0]}
    except:
        pass

    try:
        exp_cols = [r['name'] for r in query('PRAGMA table_info(exports_monthly)') if r['name'] != 'date']
        if exp_cols:
            exp = latest2('exports_monthly', exp_cols[0])
            results['exports'] = {'current': exp[0] if exp else None, 'prev': exp[1] if len(exp)>1 else None, 'column': exp_cols[0]}
    except:
        pass

    return jsonify(results)


# ── COLUMNS HELPER ────────────────────────────────────────────────────────────
@app.route('/columns/<table_name>')
def get_columns(table_name):
    allowed = query("SELECT name FROM sqlite_master WHERE type='table'")
    allowed_names = [r['name'] for r in allowed]
    if table_name not in allowed_names:
        return jsonify({'error': 'Table not found'}), 404
    cols = query(f'PRAGMA table_info("{table_name}")')
    return jsonify({'table': table_name, 'columns': [c['name'] for c in cols]})


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"\n⚠  Database not found at: {DB_PATH}")
        print("   Make sure natural_gas_energy.db is in the same folder as this script.\n")
    else:
        print(f"\n✅ Database found: {DB_PATH}")
        tables = query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        print(f"   Tables: {', '.join(r['name'] for r in tables)}\n")

    print("🚀 Starting Energy API server at http://localhost:5000")
    print("   Press Ctrl+C to stop\n")
    app.run(host='localhost', port=5000, debug=False)
