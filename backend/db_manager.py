import sqlite3
from database import Database
import sys

def show_menu():
    print("\n" + "="*60)
    print("  OPTIK FORM OKUYUCU - VERITABANI YÖNETİMİ")
    print("="*60)
    print("\n[1] Veritabanı Bilgileri")
    print("[2] Tüm Kullanıcıları Listele")
    print("[3] Tüm Cevap Anahtarlarını Listele")
    print("[4] Tüm Sonuçları Listele")
    print("[5] Test Kullanıcısı Oluştur")
    print("[6] Veritabanını Temizle")
    print("[7] Tablo Yapılarını Göster")
    print("[0] Çıkış")
    print("\nSeçiminiz: ", end="")

def show_database_info():
    """Veritabanı genel bilgileri"""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("  VERİTABANI BİLGİLERİ")
    print("="*60)
    
    tables = ['users', 'answer_keys', 'subjects', 'questions', 'student_results', 'student_answers']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table.ljust(20)} : {count} kayıt")
    
    conn.close()

def list_all_users():
    """Tüm kullanıcıları listele"""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email, full_name, created_at FROM users")
    users = cursor.fetchall()
    
    print("\n" + "="*60)
    print("  KULLANICILAR")
    print("="*60)
    
    if not users:
        print("\nHenüz kullanıcı yok!")
    else:
        print(f"\n{'ID':<5} {'Kullanıcı Adı':<15} {'Email':<25} {'Ad Soyad':<20}")
        print("-" * 80)
        for user in users:
            print(f"{user[0]:<5} {user[1]:<15} {user[2]:<25} {user[3]:<20}")
        print(f"\nToplam: {len(users)} kullanıcı")
    
    conn.close()

def list_all_answer_keys():
    """Tüm cevap anahtarlarını listele"""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ak.id, u.username, ak.exam_name, ak.school_type, 
               ak.total_questions, ak.created_at
        FROM answer_keys ak
        JOIN users u ON ak.user_id = u.id
        ORDER BY ak.created_at DESC
    """)
    keys = cursor.fetchall()
    
    print("\n" + "="*60)
    print("  CEVAP ANAHTARLARI")
    print("="*60)
    
    if not keys:
        print("\nHenüz cevap anahtarı yok!")
    else:
        print(f"\n{'ID':<5} {'Kullanıcı':<15} {'Sınav Adı':<25} {'Tip':<12} {'Soru Sayısı':<12}")
        print("-" * 80)
        for key in keys:
            print(f"{key[0]:<5} {key[1]:<15} {key[2]:<25} {key[3] or 'N/A':<12} {key[4]:<12}")
        print(f"\nToplam: {len(keys)} cevap anahtarı")
    
    conn.close()

def list_all_results():
    """Tüm sonuçları listele"""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT sr.id, sr.student_name, sr.student_number, 
               ak.exam_name, sr.total_score, sr.success_rate, sr.exam_date
        FROM student_results sr
        JOIN answer_keys ak ON sr.answer_key_id = ak.id
        ORDER BY sr.exam_date DESC
    """)
    results = cursor.fetchall()
    
    print("\n" + "="*60)
    print("  SINAV SONUÇLARI")
    print("="*60)
    
    if not results:
        print("\nHenüz sonuç yok!")
    else:
        print(f"\n{'ID':<5} {'Öğrenci Adı':<20} {'No':<10} {'Sınav':<20} {'Puan':<8} {'Başarı %':<10}")
        print("-" * 90)
        for result in results:
            print(f"{result[0]:<5} {result[1] or 'N/A':<20} {result[2] or 'N/A':<10} "
                  f"{result[3]:<20} {result[4] or 0:<8.1f} {result[5] or 0:<10.1f}")
        print(f"\nToplam: {len(results)} sonuç")
    
    conn.close()


def clear_database():
    """Veritabanını temizle"""
    print("\n" + "="*60)
    print(" VERİTABANINI TEMİZLE")
    print("="*60)
    
    print("\nUYARI: Bu işlem TÜM verileri silecektir!")
    print("\nHangi tabloları temizlemek istiyorsunuz?")
    print("[1] Sadece sonuçları sil (student_results, student_answers)")
    print("[2] Cevap anahtarları ve sonuçları sil")
    print("[3] Sadece kullanıcıları sil")
    print("[4] HER ŞEYİ SİL (tüm veriler)")
    print("[0] İptal")
    
    choice = input("\nSeçim: ")
    
    if choice == "0":
        print("İşlem iptal edildi.")
        return
    
    confirm = input("\nEmin misiniz? (EVET yazın): ")
    if confirm != "EVET":
        print("İşlem iptal edildi.")
        return
    
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        if choice == "1":
            cursor.execute("DELETE FROM student_answers")
            cursor.execute("DELETE FROM student_results")
            print("✅ Sonuçlar temizlendi.")
        
        elif choice == "2":
            cursor.execute("DELETE FROM student_answers")
            cursor.execute("DELETE FROM student_results")
            cursor.execute("DELETE FROM questions")
            cursor.execute("DELETE FROM subjects")
            cursor.execute("DELETE FROM answer_keys")
            print("✅ Cevap anahtarları ve sonuçlar temizlendi.")
        
        elif choice == "3":
            # Önce kullanıcıya bağlı verileri sil
            cursor.execute("DELETE FROM student_answers")
            cursor.execute("DELETE FROM student_results")
            cursor.execute("DELETE FROM questions")
            cursor.execute("DELETE FROM subjects")
            cursor.execute("DELETE FROM answer_keys")
            cursor.execute("DELETE FROM users")
            print("✅ Tüm kullanıcılar ve ilgili veriler temizlendi.")
        
        elif choice == "4":
            tables = ['student_answers', 'student_results', 'questions', 
                     'subjects', 'answer_keys', 'users']
            for table in tables:
                cursor.execute(f"DELETE FROM {table}")
            print("✅ Tüm veriler temizlendi.")
        
        else:
            print("❌ Geçersiz seçim!")
            return
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Hata: {e}")
    finally:
        conn.close()

def show_table_structures():
    
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("  TABLO YAPILARI")
    print("="*60)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n📋 {table_name.upper()}")
        print("-" * 60)
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"{'Sütun':<20} {'Tip':<15} {'Null?':<8} {'Varsayılan':<15}")
        print("-" * 60)
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            not_null = "NOT NULL" if col[3] else "NULL"
            default = col[4] or "-"
            print(f"{col_name:<20} {col_type:<15} {not_null:<8} {str(default):<15}")
    
    conn.close()

def main():
    """Ana program"""
    # Veritabanını initialize et
    print("\n🔄 Veritabanı kontrol ediliyor...")
    db = Database()
    print("✅ Veritabanı hazır!")
    
    while True:
        show_menu()
        choice = input()
        
        if choice == "0":
            print("\n👋 Görüşmek üzere!")
            sys.exit(0)
        
        elif choice == "1":
            show_database_info()
        
        elif choice == "2":
            list_all_users()
        
        elif choice == "3":
            list_all_answer_keys()
        
        elif choice == "4":
            list_all_results()
        
        elif choice == "5":
            create_test_user()
        
        elif choice == "6":
            clear_database()
        
        elif choice == "7":
            show_table_structures()
        
        else:
            print("❌ Geçersiz seçim!")
        
        input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandırıldı.")
        sys.exit(0)
