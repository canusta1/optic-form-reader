"""
Basit SQLite veritabanı tarayıcısı
Web arayüzü ile veritabanını görüntüle
"""
from flask import Flask, render_template_string, jsonify
import sqlite3
import json

app = Flask(__name__)
DB_NAME = 'optic_forms.db'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SQLite Veritabanı Tarayıcı</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #667eea;
            margin-bottom: 30px;
            text-align: center;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card h3 {
            font-size: 14px;
            margin-bottom: 10px;
            opacity: 0.9;
        }
        .stat-card .number {
            font-size: 32px;
            font-weight: bold;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #ddd;
        }
        .tab {
            padding: 12px 24px;
            cursor: pointer;
            background: none;
            border: none;
            font-size: 16px;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .tab:hover {
            color: #667eea;
        }
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .table-container {
            display: none;
            overflow-x: auto;
        }
        .table-container.active {
            display: block;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        tr:hover {
            background: #f5f5f5;
        }
        .empty {
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 18px;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background: #764ba2;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗄️ Optik Form Okuyucu - Veritabanı Tarayıcı</h1>
        
        <button class="refresh-btn" onclick="location.reload()">🔄 Yenile</button>
        
        <div class="stats" id="stats"></div>
        
        <div class="tabs" id="tabs"></div>
        
        <div id="tables"></div>
    </div>

    <script>
        let data = {};
        
        async function loadData() {
            const response = await fetch('/api/data');
            data = await response.json();
            renderStats();
            renderTabs();
            renderTables();
        }
        
        function renderStats() {
            const stats = document.getElementById('stats');
            stats.innerHTML = Object.keys(data.tables).map(table => `
                <div class="stat-card">
                    <h3>${table.toUpperCase()}</h3>
                    <div class="number">${data.tables[table].length}</div>
                </div>
            `).join('');
        }
        
        function renderTabs() {
            const tabs = document.getElementById('tabs');
            tabs.innerHTML = Object.keys(data.tables).map((table, i) => `
                <button class="tab ${i === 0 ? 'active' : ''}" 
                        onclick="showTable('${table}')">${table}</button>
            `).join('');
        }
        
        function renderTables() {
            const container = document.getElementById('tables');
            container.innerHTML = Object.entries(data.tables).map(([table, rows], i) => {
                if (rows.length === 0) {
                    return `
                        <div class="table-container ${i === 0 ? 'active' : ''}" id="table-${table}">
                            <div class="empty">📭 Bu tabloda veri yok</div>
                        </div>
                    `;
                }
                
                const columns = Object.keys(rows[0]);
                return `
                    <div class="table-container ${i === 0 ? 'active' : ''}" id="table-${table}">
                        <table>
                            <thead>
                                <tr>${columns.map(col => `<th>${col}</th>`).join('')}</tr>
                            </thead>
                            <tbody>
                                ${rows.map(row => `
                                    <tr>${columns.map(col => `<td>${row[col] ?? '-'}</td>`).join('')}</tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            }).join('');
        }
        
        function showTable(tableName) {
            // Tüm tabları gizle
            document.querySelectorAll('.table-container').forEach(el => {
                el.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(el => {
                el.classList.remove('active');
            });
            
            // Seçili tabloyu göster
            document.getElementById('table-' + tableName).classList.add('active');
            event.target.classList.add('active');
        }
        
        loadData();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    """Tüm veritabanı verilerini döndür"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    tables = ['users', 'answer_keys', 'subjects', 'questions', 'student_results', 'student_answers']
    result = {'tables': {}}
    
    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            result['tables'][table] = [dict(row) for row in rows]
        except Exception as e:
            result['tables'][table] = []
    
    conn.close()
    return jsonify(result)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  VERİTABANI TARAYICI WEB ARAYÜZÜ")
    print("="*60)
    print("\n📡 Tarayıcınızda açın: http://127.0.0.1:5001")
    print("🔄 Sayfayı yenileyerek güncel verileri görüntüleyin")
    print("⏹️  Durdurmak için Ctrl+C\n")
    
    app.run(debug=True, port=5001, host='0.0.0.0')
