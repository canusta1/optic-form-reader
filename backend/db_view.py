"""
Veritabanı Görüntüleyici
Kullanım: python db_view.py [tablo_adı]
"""
import sqlite3
import sys

def show_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    print("\n📊 TABLOLAR:")
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"   - {t} ({count} kayıt)")
    return tables

def show_table_content(cursor, table_name, limit=10):
    print(f"\n📋 {table_name.upper()} (son {limit} kayıt):")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"   Kolonlar: {columns}")
    
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT {limit}")
    rows = cursor.fetchall()
    
    for row in rows:
        print(f"\n   ID: {row[0]}")
        for i, col in enumerate(columns[1:], 1):
            val = str(row[i])[:100] + "..." if len(str(row[i])) > 100 else row[i]
            print(f"      {col}: {val}")

def main():
    conn = sqlite3.connect('optic_forms.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    tables = show_tables(cursor)
    
    if len(sys.argv) > 1:
        table = sys.argv[1]
        if table in tables:
            show_table_content(cursor, table)
        else:
            print(f"\n❌ '{table}' tablosu bulunamadı!")
    else:
        print("\n💡 Belirli bir tabloyu görmek için: python db_view.py tablo_adı")
        print("   Örnek: python db_view.py users")
        print("          python db_view.py student_results")
    
    conn.close()

if __name__ == "__main__":
    main()
