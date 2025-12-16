import os
import sys
from database import Database
from image_processor import OptikFormOkuyucu
from app import compare_answers

db = Database()

# Cevap anahtarı ID'si (test_grading_system.py'den)
answer_key_id = 3

# Formu oku
okuyucu = OptikFormOkuyucu(debug_mode=False)
sonuc = okuyucu.form_oku("debug_images/0_orijinal.jpg")

if sonuc['success']:
    print("Tespit edilen cevaplar (ilk 15):")
    for i in range(1, 16):
        print(f"  {i}: {sonuc['answers'].get(i, 'YOK')}")
    
    # DB'den cevap anahtarı
    answer_key_details = db.get_answer_key_details(answer_key_id)
    
    print("\nCevap anahtarı yapısı:")
    print(f"  Ders sayısı: {len(answer_key_details['subjects'])}")
    
    for subj in answer_key_details['subjects']:
        print(f"  - {subj['subject_name']}: {len(subj['answers'])} soru")
        print(f"    İlk 5 cevap: {subj['answers'][:5]}")
    
    # Manuel karşılaştır
    print("\nManuel karşılaştırma (ilk 15):")
    question_counter = 1
    dogru = 0
    for subject in answer_key_details['subjects']:
        for i, correct in enumerate(subject['answers']):
            student = sonuc['answers'].get(question_counter, 'BOŞ')
            eslesme = "✓" if student == correct else ""
            if student == correct:
                dogru += 1
            if question_counter <= 15:
                print(f"  Soru {question_counter}: Anahtar={correct}, Öğrenci={student} {eslesme}")
            question_counter += 1
    
    print(f"\nToplam doğru: {dogru}/160")
