import os
import sys
import cv2
import numpy as np
from database import Database
from image_processor import OptikFormOkuyucu
from app import compare_answers

def test_grading_system():
    print("\n" + "="*60)
    print("  OPTİK FORM OKUMA VE PUANLAMA SİSTEMİ TESTİ")
    print("="*60)
    
    # 1. Veritabanı Hazırlığı
    print("\n1. Veritabanı kontrol ediliyor...")
    db = Database()
    
    # Test kullanıcısı oluştur/bul
    user_id = db.create_user('test_user', 'test@example.com', '123456', 'Test Kullanıcı')
    if not user_id:
        # Kullanıcı zaten varsa ID'sini bul
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = 'test_user'")
        user_id = cursor.fetchone()[0]
        conn.close()
    print(f"   ✅ Kullanıcı ID: {user_id}")
    
    # Test cevap anahtarı oluştur
    exam_name = "YGS Deneme Sınavı - Test"
    school_type = "Lise"
    
    # Örnek cevap anahtarı verisi
    subjects_data = [
        {
            'name': 'Türkçe',
            'question_count': 40,
            'points_per_question': 4.0,
            'answers': ['A', 'B', 'C', 'D', 'E'] * 8,  # 40 soru
            'points': [4.0] * 40  # Her soru 4 puan
        },
        {
            'name': 'Matematik',
            'question_count': 40,
            'points_per_question': 4.0,
            'answers': ['A', 'B', 'C', 'D', 'E'] * 8,
            'points': [4.0] * 40
        },
        {
            'name': 'Fen Bilimleri',
            'question_count': 40,
            'points_per_question': 4.0,
            'answers': ['A', 'B', 'C', 'D', 'E'] * 8,
            'points': [4.0] * 40
        },
        {
            'name': 'Sosyal Bil.',
            'question_count': 40,
            'points_per_question': 4.0,
            'answers': ['A', 'B', 'C', 'D', 'E'] * 8,
            'points': [4.0] * 40
        }
    ]
    
    # Önce bu isimde bir sınav var mı kontrol et
    existing_key = db.get_answer_key_by_name(user_id, exam_name)
    if existing_key:
        answer_key_id = existing_key['id']
        print(f"   ✅ Mevcut Cevap Anahtarı Kullanılıyor (ID: {answer_key_id})")
    else:
        answer_key_id = db.create_answer_key(user_id, exam_name, school_type, subjects_data)
        print(f"   ✅ Yeni Cevap Anahtarı Oluşturuldu (ID: {answer_key_id})")
    
    # 2. Görüntü İşleme
    print("\n2. Optik form okunuyor...")
    image_path = "debug_images/0_orijinal.jpg"
    
    if not os.path.exists(image_path):
        print(f"   ❌ Hata: Test görüntüsü bulunamadı ({image_path})")
        return
        
    okuyucu = OptikFormOkuyucu(debug_mode=True)
    sonuc = okuyucu.form_oku(image_path)
    
    if not sonuc['success']:
        print(f"   ❌ Okuma hatası: {sonuc.get('error')}")
        return
        
    print(f"   ✅ Form başarıyla okundu")
    print(f"   👤 Öğrenci: {sonuc['student_info']['name']} {sonuc['student_info']['surname']}")
    print(f"   📝 Toplam {len(sonuc['answers'])} cevap tespit edildi")
    
    # 3. Puanlama
    print("\n3. Puanlama yapılıyor...")
    
    # DB'den cevap anahtarı detaylarını çek
    answer_key_details = db.get_answer_key_details(answer_key_id)
    
    # Karşılaştır
    karsilastirma = compare_answers(answer_key_details, sonuc['answers'])
    
    print(f"\n   📊 SONUÇLAR:")
    print(f"   Toplam Puan: {karsilastirma['total_score']}")
    print(f"   Doğru Sayısı: {karsilastirma['correct_count']}")
    print(f"   Başarı Oranı: %{karsilastirma['success_rate']}")
    
    print("\n   Ders Bazlı Sonuçlar:")
    for ders, skor in karsilastirma['subject_scores'].items():
        print(f"   - {ders}: {skor['correct']}/{skor['total']} Doğru ({skor['score']} Puan)")
        
    # 4. Kayıt
    print("\n4. Sonuçlar kaydediliyor...")
    student_data = {
        'name': f"{sonuc['student_info']['name']} {sonuc['student_info']['surname']}",
        'number': '12345',
        'total_score': karsilastirma['total_score'],
        'success_rate': karsilastirma['success_rate']
    }
    
    result_id = db.save_student_result(
        answer_key_id,
        student_data,
        karsilastirma['detailed_answers'],
        image_path
    )
    print(f"   ✅ Sonuç ID: {result_id} ile kaydedildi")
    
    print("\n" + "="*60)
    print("  TEST BAŞARIYLA TAMAMLANDI")
    print("="*60)

if __name__ == "__main__":
    test_grading_system()