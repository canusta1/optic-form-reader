import sqlite3
import json

conn = sqlite3.connect('optik_form.db')
cursor = conn.cursor()

# Tabloları listele
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("Tablolar:", tables)

# forms tablosundan cevap anahtarını al
cursor.execute('SELECT cevap_anahtari FROM forms ORDER BY id DESC LIMIT 1')
row = cursor.fetchone()
if row:
    cevap_anahtari = json.loads(row[0]) if row[0] else {}
    turkce_key = cevap_anahtari.get('turkce', {})
    print("\nCevap Anahtari (Türkçe ilk 15):")
    for i in range(1, 16):
        print(f"  Soru {i}: {turkce_key.get(str(i), 'YOK')}")

# Son sonucu al
cursor.execute('SELECT turkce_cevaplar FROM results ORDER BY id DESC LIMIT 1')
row = cursor.fetchone()
if row:
    turkce_ans = json.loads(row[0]) if row[0] else {}
    print("\nTespit Edilen (Türkçe ilk 15):")
    for i in range(1, 16):
        print(f"  Soru {i}: {turkce_ans.get(str(i), 'YOK')}")

# Eşleşme kontrolü
print("\nEşleşme Kontrolü:")
dogru = 0
for i in range(1, 41):
    key = turkce_key.get(str(i), '')
    ans = turkce_ans.get(str(i), '')
    eslesme = "✓" if key == ans and key != 'BOŞ' else ""
    if key == ans and key != 'BOŞ':
        dogru += 1
    if i <= 15:
        print(f"  Soru {i}: Anahtar={key}, Tespit={ans} {eslesme}")

print(f"\nToplam Doğru: {dogru}/40")
conn.close()
